"""S.O.U.L. agent loop — ReAct (Thought→Action→Observation) + Reflexion retry + send-gates.

run(goal) -> {"status": "done", "answer", "trace"}
          -> {"status": "awaiting_approval", "pending": {...}, "trace"}
resume(pid, approved) -> continues a paused run after the user decides.
"""
import time
import uuid
import budget
import config
import llm
import memory
import tools

_pending = {}  # pid -> {"messages","trace","step","tool","args","goal","toolset","confirm"}


def _mem_block(goal):
    lines = memory.recall(goal)
    if not lines:
        return ""
    return "\nRelevant past lessons:\n- " + "\n- ".join(lines) + "\n"


def _step_once(messages, trace, step, goal, toolset, confirm_set, describe):
    """Run model turns until answer OR gated send. Returns (outcome, data)."""
    fails = 0
    while step < config.MAX_STEPS:
        step += 1
        try:
            budget.tick()  # no-op unless a ticket budget is active
        except budget.BudgetExceeded as e:
            trace.append({"type": "error", "text": str(e)})
            return ("error", f"{e}. Ticket too big or loop spinning — dispatcher notified.")
        try:
            out = llm.chat(messages)
        except Exception as e:
            trace.append({"type": "error", "text": f"model error: {e}"})
            return ("error", f"Brain unreachable ({e}). Is Ollama up / MODEL={config.MODEL} pulled?")
        thought = out.get("thought", "")
        if "answer" in out and "tool" not in out:
            ans = out["answer"] or ""
            if '"tool"' in ans and '"input"' in ans:
                trace.append({"type": "thought", "text": thought})
                obs = ("PROTOCOL VIOLATION: you wrote tool calls as text. "
                       "Emit exactly ONE JSON object with a single tool call instead.")
                trace.append({"type": "observation", "tool": "protocol", "text": obs})
                trace.append({"type": "leak", "text": ans[: 400]})
                messages += [{"role": "assistant", "content": f"THOUGHT: {thought}"},
                             {"role": "user", "content": f"OBSERVATION: {obs}"}]
                fails += 1
                if fails >= config.MAX_RETRIES:
                    return ("error", "I tangled my own reasoning loop. Try rephrasing the request.")
                continue
            trace.append({"type": "thought", "text": thought})
            trace.append({"type": "answer", "text": ans})
            return ("done", ans)
        tool, args = out.get("tool"), out.get("input", {}) or {}
        trace.append({"type": "thought", "text": thought})
        if tool not in toolset:
            obs = f"Error: unknown tool '{tool}'. Available: {', '.join(toolset)}."
            trace.append({"type": "observation", "tool": tool or "?", "text": obs})
            messages += [{"role": "assistant", "content": f"THOUGHT: {thought}"},
                         {"role": "user", "content": f"OBSERVATION: {obs}"}]
            fails += 1
            if fails >= config.MAX_RETRIES:
                return ("error", "Kept requesting unknown tools. Stopping.")
            continue
        if tool in confirm_set:
            pid = uuid.uuid4().hex[: 8]
            _pending[pid] = {"messages": messages, "trace": trace, "step": step,
                             "tool": tool, "args": args, "goal": goal,
                             "toolset": toolset, "confirm": confirm_set,
                             "describe": describe}
            trace.append({"type": "gate", "tool": tool, "text": _draft(tool, args), "pid": pid})
            return ("gate", pid)
        trace.append({"type": "action", "tool": tool, "text": describe.get(tool, tool)})
        try:
            obs = toolset[tool](args)
        except Exception as e:
            obs = f"Error running {tool}: {e}"
        trace.append({"type": "observation", "tool": tool, "text": obs})
        messages += [{"role": "assistant", "content": f"THOUGHT: {thought} ACTION: {tool}"},
                     {"role": "user", "content": f"OBSERVATION ({tool}): {obs}"}]
    return ("error", f"Hit step cap ({config.MAX_STEPS}). Goal too big — break it down?")


def _draft(tool, args):
    if tool == "gmail_send":
        return f"To: {args.get('to')}\nSubject: {args.get('subject')}\n\n{args.get('body')}"
    if tool == "wa_send":
        return f"To: {args.get('to')}\n\n{args.get('text')}"
    return str(args)


def run_native(goal, toolset, describe, schemas, system, max_steps=None):
    """Builder-grade loop with NATIVE function calling.

    Same trace format as run() so the UI is untouched. No JSON-in-text:
    file payloads travel as typed tool args. Unknown tools and errors
    become observations, same Reflexion discipline.
    """
    max_steps = max_steps or config.MAX_STEPS
    trace = [{"type": "thought", "text": f"Goal accepted: {goal}"}]
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": f"GOAL: {goal}{_mem_block(goal)}"}]
    step, fails = 0, 0
    while step < max_steps:
        step += 1
        try:
            budget.tick()
        except budget.BudgetExceeded as e:
            trace.append({"type": "error", "text": str(e)})
            return {"status": "error", "answer": f"{e}. Ticket too big or loop spinning.", "trace": trace}
        try:
            text, calls = llm.chat_native(messages, schemas)
        except Exception as e:
            trace.append({"type": "error", "text": f"model error: {e}"})
            return {"status": "error", "answer": f"Brain unreachable ({e}).", "trace": trace}
        if text.strip():
            trace.append({"type": "thought", "text": text.strip()[: 500]})
        valid = [c for c in calls if c["name"] in toolset]
        for c in calls:
            if c["name"] not in toolset:
                obs = f"Error: unknown tool '{c['name']}'. Available: {', '.join(toolset)}."
                trace.append({"type": "observation", "tool": c["name"], "text": obs})
                fails += 1
        if not valid:
            if not text.strip():
                # Empty finish: model stalled. Nudge, don't accept.
                trace.append({"type": "thought", "text": "(empty turn — nudged)"})
                messages.append({"role": "user", "content": "OBSERVATION: empty response — call a tool to make progress or give the final answer."})
                fails += 1
                if fails >= config.MAX_RETRIES:
                    return {"status": "error", "answer": "Stalled with empty responses.", "trace": trace}
                continue
            if fails >= config.MAX_RETRIES:
                return {"status": "error", "answer": "Kept requesting unknown tools.", "trace": trace}
            trace.append({"type": "answer", "text": text})
            return {"status": "done", "answer": text or "(empty finish)", "trace": trace}
        messages.append({"role": "assistant", "content": text or "", "tool_calls": [
            {"function": {"name": c["name"], "arguments": c["args"]}} for c in valid]})
        for c in valid:
            tool, args = c["name"], c["args"] if isinstance(c["args"], dict) else {}
            trace.append({"type": "action", "tool": tool, "text": describe.get(tool, tool)})
            try:
                obs = toolset[tool](args)
            except Exception as e:
                obs = f"Error running {tool}: {e}"
            trace.append({"type": "observation", "tool": tool, "text": obs})
            messages.append({"role": "tool", "content": str(obs)[: config.MAX_OBS_CHARS]})
    return {"status": "error",
            "answer": f"Hit step cap ({max_steps}). Goal too big — break it down?",
            "trace": trace}


def run(goal, toolset=None, describe=None, system=None, confirm=None):
    """goal: str. Optional crew overrides: restricted toolset + role prompt.
    Defaults = full S.O.U.L. assistant behavior."""
    toolset = toolset or tools.TOOLS
    describe = describe or tools.DESCRIBE
    system = system or llm.SYSTEM_PROMPT
    confirm = set(confirm) if confirm is not None else set(config.CONFIRM_TOOLS)
    trace = [{"type": "thought", "text": f"Goal accepted: {goal}"}]
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"GOAL: {goal}{_mem_block(goal)}"},
    ]
    outcome, data = _step_once(messages, trace, 0, goal, toolset, confirm, describe)
    if outcome == "done":
        return {"status": "done", "answer": data, "trace": trace}
    if outcome == "gate":
        p = _pending[data]
        return {"status": "awaiting_approval",
                "pending": {"id": data, "tool": p["tool"], "args": p["args"],
                            "draft": _draft(p["tool"], p["args"])},
                "trace": trace}
    return {"status": "error", "answer": data, "trace": trace}


def pending_info(pid):
    p = _pending.get(pid)
    if not p:
        return None
    return {"id": pid, "tool": p["tool"], "args": p["args"], "draft": _draft(p["tool"], p["args"])}


def resume(pid, approved):
    p = _pending.pop(pid, None)
    if not p:
        return {"status": "error", "answer": "Approval expired or unknown.", "trace": []}
    messages, trace, step = p["messages"], p["trace"], p["step"]
    toolset, confirm, describe = p["toolset"], p["confirm"], p["describe"]
    if approved:
        try:
            obs = toolset[p["tool"]](p["args"])
        except Exception as e:
            obs = f"Error running {p['tool']}: {e}"
        trace.append({"type": "action", "tool": p["tool"], "text": f"APPROVED — {describe.get(p['tool'], p['tool'])}"})
        if "error" in obs.lower()[: 30] or obs.startswith("Error"):
            memory.remember("lesson", f"{p['tool']} failed: {obs[:200]}")
    else:
        obs = "CANCELLED by user — the send was not executed."
        trace.append({"type": "action", "tool": p["tool"], "text": "DENIED by user — send skipped"})
    messages += [{"role": "assistant", "content": f"ACTION (approved={approved}): {p['tool']}"},
                 {"role": "user", "content": f"OBSERVATION ({p['tool']}): {obs}"}]
    outcome, data = _step_once(messages, trace, step, p["goal"], toolset, confirm, describe)
    if outcome == "done":
        return {"status": "done", "answer": data, "trace": trace}
    if outcome == "gate":
        q = _pending[data]
        return {"status": "awaiting_approval",
                "pending": {"id": data, "tool": q["tool"], "args": q["args"],
                            "draft": _draft(q["tool"], q["args"])},
                "trace": trace}
    return {"status": "error", "answer": data, "trace": trace}
