"""S.O.U.L. Agency — the crew. Centralized dispatcher + verified handoffs.

Roles (bounded, code-driven — agents never free-chat):
  SCOUT    researcher/architect: web + notes -> build plan (oneshot)
  BUILDER  developer: writes files into workspace/<tid>/ via restricted ReAct loop
  SENTINEL reviewer/QA: deterministic code_check + LLM verdict PASS/FAIL
Dispatcher run_ticket() enforces: OPEN->PLANNED->BUILDING->REVIEWING->DONE,
with FAIL notes routed back to BUILDING (max 2 retries) else FAILED.
"""
import json
import json
import os
import threading
import time
import budget
import config
import health
import llm
import agent
import memory
import tickets
import tools

MAX_BUILD_RETRIES = 2
BUDGET_PER_TICKET = 25  # max model calls per ticket (token-burn fuse)

SCOUT_SYSTEM = """You are SCOUT, research architect of the S.O.U.L. agency.
Given a ticket, research what is needed and output EXACTLY ONE JSON object:
{"thought": "<research reasoning>",
 "plan": "<numbered build plan: exact files to create, content outline, design notes>",
 "acceptance": ["<checkable criterion 1>", "<criterion 2>", ...]}
Rules for acceptance criteria: 3-6 items, each objectively checkable against
files (e.g. "index.html exists and is >2KB", "no TODO/FIXME/lorem placeholders",
"no embedded secrets"). They are the contract SENTINEL will verify. English only.
Criteria style rules (brittle criteria kill good builds): prefer MINIMUMS over
exact counts ("at least 6 gallery blocks", not "exactly six .photo divs");
name elements loosely ("a hero section naming the subject", not exact strings);
never demand what you cannot check from files alone."""

BUILDER_SYSTEM = """You are BUILDER, developer of the S.O.U.L. agency.
You implement the approved plan by writing files with workspace_write.
EVERY reply must be EXACTLY ONE JSON object, no other text.
To act: {"thought": "<why>", "tool": "<tool>", "input": {<args>}}
To finish: {"thought": "<what was built>", "answer": "<list of files written>"}
TOOLS:
- workspace_write {"path": "<tid>/file", "content": "<FULL file content>"} — write files, always under the ticket folder
- workspace_read {"path": "<tid>/file"} — re-read to verify
- workspace_list {"prefix": "<tid>/"} — list ticket files
- web_fetch {"url": "..."} — reference lookup only
- calculator {"expression": "..."} — if numbers needed
RULES: one tool per turn; write COMPLETE files (no stubs, no TODO, no lorem);
single self-contained .html with inline CSS/JS beats multi-file sprawl for sites;
never write secrets; verify with workspace_read before finishing."""

BUILDER_TOOLS = {k: tools.TOOLS[k] for k in
                 ("workspace_write", "workspace_read", "workspace_list", "web_fetch", "calculator")}
BUILDER_DESCRIBE = {k: tools.DESCRIBE[k] for k in BUILDER_TOOLS}
BUILDER_SCHEMAS = [
    {"name": "workspace_write", "description": "Write a COMPLETE file inside workspace/. Always use paths under the ticket folder.",
     "args": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
    {"name": "workspace_read", "description": "Read a file inside workspace/ to verify it.",
     "args": {"path": {"type": "string"}}, "required": ["path"]},
    {"name": "workspace_list", "description": "List files inside workspace/.",
     "args": {"prefix": {"type": "string"}}},
    {"name": "web_fetch", "description": "Reference lookup: read a web page as text.",
     "args": {"url": {"type": "string"}}, "required": ["url"]},
    {"name": "calculator", "description": "Arithmetic if numbers are needed.",
     "args": {"expression": {"type": "string"}}, "required": ["expression"]},
]
BUILDER_SYSTEM_NATIVE = """You are BUILDER, developer of the S.O.U.L. agency.
Implement the ticket goal by calling tools. Write COMPLETE files under the
ticket folder (no stubs, no TODO, no lorem, never any secrets). Verify by
reading files back. When done, reply with plain text listing files written."""

SENTINEL_SYSTEM = """You are SENTINEL, reviewer of the S.O.U.L. agency.
Given the acceptance criteria, the code_check report and file listing, output
EXACTLY ONE JSON object:
{"thought": "<review reasoning>", "verdict": "PASS|FAIL",
 "criteria_met": [true/false per criterion, in order],
 "notes": "<concrete issues or 'clean'>"}
Rules (communicative dehallucination: be specific or be silent):
- PASS only if EVERY criterion is met by real files. No vibes.
- FAIL notes must cite file:line + expected vs actual, one issue per line.
- FAIL on: syntax failures, embedded secrets, placeholders/stubs, empty files."""


def scout(tid, ticket):
    out = llm.oneshot(SCOUT_SYSTEM,
                      f"Ticket {tid}: {ticket['title']}\nDetails: {ticket['description']}\n"
                      f"Ticket folder: workspace/{tid}/")
    plan = out.get("plan", out.get("answer", str(out)))
    criteria = out.get("acceptance") or []
    if isinstance(criteria, str):
        criteria = [criteria]
    tickets.transition(tid, "PLANNED", f"plan by SCOUT ({len(plan)} chars, {len(criteria)} criteria)",
                       {"plan": plan, "acceptance": criteria})
    return plan, criteria


def builder(tid, ticket, plan, criteria, feedback="", must_rewrite=False):
    crit = "\n".join(f"- {c}" for c in criteria)
    goal = (f"Implement ticket {tid}: {ticket['title']}\nPlan:\n{plan[:1800]}\n"
            f"Acceptance criteria (ALL must hold when you finish):\n{crit}\n"
            f"Write ALL files under workspace/{tid}/ ."
            + (f"\nReviewer feedback from last round (FIX ALL OF IT):\n{feedback}" if feedback else "")
            + ("\nREBUILD ROUND: the last build was rejected. Call workspace_write "
               "with corrected FULL file content." if must_rewrite else ""))
    # Native function calling: file payloads travel as typed args, immune to
    # JSON-escaping failures that break text-protocol writes.
    res = agent.run_native(goal, BUILDER_TOOLS, BUILDER_DESCRIBE,
                           BUILDER_SCHEMAS, BUILDER_SYSTEM_NATIVE, max_steps=12)
    tickets.note(tid, f"builder: {res['status']} — {(res.get('answer') or '')[:200]}")
    tickets.set_artifact(tid, "trace", [
        {"t": e.get("type"), "tool": e.get("tool", ""), "text": (e.get("text") or "")[: 300]}
        for e in res.get("trace", [])])
    return res


def sentinel(tid, ticket, criteria):
    report = tools.code_check(f"{tid}/")
    listing = tools.workspace_list(f"{tid}/")
    crit = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(criteria)) or "(no criteria)"
    # Grounding (RCI-style): judge sees actual file CONTENT, not just reports.
    contents = []
    for line in listing.splitlines()[:3]:
        rel = line.split(" (")[0]
        if rel.endswith((".html", ".py", ".js", ".css", ".md", ".json")) and "pycache" not in rel:
            body = tools.workspace_read(f"{rel}")
            contents.append(f"--- {rel} ---\n{body[:2500]}")
    content_block = "\n".join(contents) or "(no readable files)"
    out = llm.oneshot(SENTINEL_SYSTEM,
                      f"Ticket {tid}: {ticket['title']}\nAcceptance criteria:\n{crit}\n"
                      f"Files:\n{listing}\nCheck report:\n{report}\n"
                      f"File contents:\n{content_block}")
    verdict = (out.get("verdict") or "FAIL").upper()
    notes = out.get("notes", out.get("answer", ""))
    met = out.get("criteria_met", [])
    if verdict.startswith("PASS") and any(m is False for m in met if isinstance(m, bool)):
        verdict = "FAIL"  # model said PASS but admitted unmet criteria: trust the evidence
        notes = f"(auto-downgraded: criteria_met={met}) {notes}"
    return ("PASS" if verdict.startswith("PASS") else "FAIL", notes, report)


def _autosave_skill(tid, ticket, plan, criteria, review):
    """Voyager-style learning: every shipped ticket becomes a reusable
    SKILL.md (trigger + process + constraints), no extra model call."""
    import time as _t
    d = os.path.join(config.BASE_DIR, "skills", f"auto-{tid.lower()}")
    os.makedirs(d, exist_ok=True)
    crit = "\n".join(f"- {c}" for c in criteria)
    body = (f"# Skill: {ticket['title']} (auto-learned from {tid})\n\n"
            f"## Trigger\nUser asks for something like: {ticket['title']}.\n"
            f"Original request: {ticket.get('description', '')[:300]}\n\n"
            f"## Process\n{plan[:2000]}\n\n"
            f"## Output constraints\n{crit}\n\n"
            f"## Provenance\nLearned {_t.strftime('%Y-%m-%d')} from ticket {tid}.\n"
            f"Reviewer verdict: {str(review)[:300]}\n")
    fp = os.path.join(d, "SKILL.md")
    with open(fp, "w", encoding="utf-8") as f:
        f.write(body)
    return fp


def run_ticket(tid):
    """Dispatcher: drive one ticket through the line. Returns final ticket.
    Wraps the run in a per-ticket model-call budget and logs PC load."""
    t = tickets.get(tid)
    if not t:
        return None
    budget.start(BUDGET_PER_TICKET)
    try:
        before = health.snapshot()
        tickets.note(tid, f"dispatch: load cpu={before['cpu']}% mem={before['mem']['used_pct']}%")
        plan, criteria = scout(tid, t)
        tickets.transition(tid, "BUILDING", "dispatched to BUILDER")
        last_notes = ""
        for attempt in range(1, MAX_BUILD_RETRIES + 2):
            # Fresh retry if the Builder tangled its own loop (transient model flake,
            # not a verdict): same round, no penalty, up to 2 extra shots.
            res, tangles = None, 0
            while tangles < 2:
                res = builder(tid, tickets.get(tid), plan, criteria,
                              feedback="" if attempt == 1 else last_notes,
                              must_rewrite=(attempt > 1))
                if res["status"] == "done" or "tangled" not in (res.get("answer") or ""):
                    break
                tangles += 1
                tickets.note(tid, f"builder loop-tangle, fresh retry {tangles}/2")
            if res["status"] != "done":
                tickets.transition(tid, "FAILED", f"builder error: {res.get('answer')}")
                return tickets.get(tid)
            tickets.transition(tid, "REVIEWING", f"build round {attempt} -> SENTINEL")
            verdict, last_notes, report = sentinel(tid, tickets.get(tid), criteria)
            if verdict == "PASS":
                after = health.snapshot()
                tickets.transition(tid, "DONE", f"accepted: {last_notes[:200]}",
                                   {"review": last_notes, "check": report,
                                    "model_calls": budget.usage(),
                                    "load_after": f"cpu={after['cpu']}% mem={after['mem']['used_pct']}%"})
                skill_path = _autosave_skill(tid, t, plan, criteria, last_notes)
                tickets.set_artifact(tid, "skill", skill_path)
                memory.remember("reflection", f"Ticket {tid} ({t['title']}) shipped: {last_notes[:200]}")
                return tickets.get(tid)
            if attempt <= MAX_BUILD_RETRIES:
                tickets.transition(tid, "BUILDING", f"SENTINEL FAIL -> rebuild: {last_notes[:200]}")
            else:
                tickets.transition(tid, "FAILED", f"SENTINEL FAIL x{attempt}: {last_notes[:300]}",
                                   {"review": last_notes, "check": report,
                                    "model_calls": budget.usage()})
                return tickets.get(tid)
    except budget.BudgetExceeded as e:
        tickets.transition(tid, "FAILED", f"token budget blown: {e}")
    except Exception as e:
        tickets.transition(tid, "FAILED", f"dispatcher exception: {e}")
    finally:
        budget.end()
    return tickets.get(tid)


def run_queue(tids=None, max_parallel=2):
    """Adaptive dispatcher: health-gated parallelism.

    Before each wave, ask health.advice(): 2 normal / 1 warm / 0 critical.
    Critical -> sleep and re-check (max 5 pauses), never stack work on a
    melting laptop. Sequential within a wave via threads; waves repeat
    until the queue drains.
    """
    from concurrent.futures import ThreadPoolExecutor
    pending = list(tids or [t["id"] for t in tickets.list_all("OPEN")])
    if not pending:
        return []
    done, pauses = [], 0
    while pending:
        snap = health.snapshot()
        n = min(max_parallel, health.advice(snap))
        if n <= 0:
            pauses += 1
            tickets.note(pending[0], f"dispatcher paused: pressure {health.score(snap)} (pause {pauses})")
            if pauses > 5:
                for tid in pending:
                    tickets.note(tid, "dispatcher: laptop too hot, tickets left OPEN")
                break
            time.sleep(20)
            continue
        wave, pending = pending[:n], pending[n:]
        tickets.note(wave[0], f"wave of {len(wave)}: cpu={snap['cpu']}% mem={snap['mem']['used_pct']}%")
        with ThreadPoolExecutor(max_workers=len(wave)) as ex:
            for t in ex.map(run_ticket, wave):
                done.append(t["id"] if t else "?")
    return done
