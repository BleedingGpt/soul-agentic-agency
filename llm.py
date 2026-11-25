"""S.O.U.L. model client — one code path for ANY model via Ollama /api/chat.

Prompt-based JSON ReAct (not provider function-calling APIs) so the brain
is swappable with a single env var: local llama3.2:3b today, a *-cloud
model tomorrow, Groq/Gemini via an OpenAI-compatible gateway later.
"""
import json
import re
import requests
import config

SYSTEM_PROMPT = """You are S.O.U.L. — Sacrifice Outweighs Ultimate Leverage.
A smart personal assistant agent. Character over raw power: you work,
optimize, and yield for the user. You never guess when you can verify,
and you never send anything outward without explicit approval.

You reason in a loop. EVERY reply must be EXACTLY ONE JSON object, no other text.

To act: {"thought": "<why this step>", "tool": "<tool>", "input": {<args>}}
To answer: {"thought": "<final reasoning>", "answer": "<reply to user>"}

TOOLS:
- gmail_search {"query": "..."} — search inbox (Gmail syntax ok)
- gmail_send {"to": "a@b.com", "subject": "...", "body": "..."} — NEEDS user approval, only propose it
- wa_chats {"limit": 8} — recent WhatsApp chats
- wa_read {"chat": "Name", "limit": 10} — read a chat (buffered since daemon connected)
- wa_send {"to": "Name", "text": "..."} — NEEDS user approval, only propose it
- calculator {"expression": "17*23+100"} — arithmetic only, digits and + - * / ( ) . and spaces
- notes_search {"query": "..."} — search the user's personal study notes vault
- save_note {"title": "short-slug", "text": "..."} — WRITE a timestamped note into the vault (world-writing)
- web_fetch {"url": "https://..."} — read any web page as plain text (world-reading)
- remember {"kind": "lesson|reflection", "text": "..."} — store what you learned in long-term memory (self-learning)

RULES:
- One tool per turn. After an observation, reconsider before the next step.
- Prefer read-only tools first. Propose sends only when the user asked for an outward action.
- If a tool errors, say so in thought and try a different approach (max 3 retries of the same failing idea).
- Keep answers short, direct, no fluff. English only.
- ACT LIKE AN AGENT, NOT AN ASSISTANT: when a goal needs several steps
  (fetch → summarize → save → remember), do them all without asking between
  steps. Only outward-facing sends stop for approval; everything else you do.
- When you learn something durable (a fact about the user, a fixed mistake,
  a reusable procedure), call remember. When a goal produces a keepable
  result, call save_note. Leave the world better than you found it.
- PROTOCOL IS LAW: output exactly ONE JSON object per turn. NEVER write tool
  calls as plain text. NEVER narrate future steps ("Awaiting...", "Next I
  will..."). NEVER simulate or invent an observation — real observations
  arrive as user messages starting with OBSERVATION. If you catch yourself
  writing anything outside the single JSON object, stop and emit only the object.

EXAMPLE:
User goal: What is (17*23)+100?
You reply: {"thought": "Need arithmetic, use calculator.", "tool": "calculator", "input": {"expression": "(17*23)+100"}}
Observation: 491
You reply: {"thought": "Have the result.", "answer": "491"}"""


def _post(path, payload, timeout):
    """POST with backoff on transient cloud failures (500/429). Parallel
    dispatcher workers can stampede rate limits — this staggers them."""
    import time as _t
    last = None
    for wait in (2, 5, 10):
        try:
            r = requests.post(f"{config.OLLAMA_URL}{path}", json=payload, timeout=timeout)
            if r.status_code in (429,) or r.status_code >= 500:
                last = f"{r.status_code} {r.reason}"
                _t.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except requests.exceptions.Timeout:
            last = "timeout"
            _t.sleep(wait)
    # final attempt, let it raise honestly
    r = requests.post(f"{config.OLLAMA_URL}{path}", json=payload, timeout=timeout)
    r.raise_for_status()
    return r


def _extract_json(text):
    """Tolerant JSON extraction: raw, fenced, or embedded.

    Scans for balanced {...} candidates and returns the FIRST one that
    parses to a dict. Any protocol shape accepted (agent tool/answer,
    Scout plan/acceptance, Sentinel verdict) — callers validate keys.
    """
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    hay = m.group(1) if m else text
    depth, start = 0, -1
    for i, ch in enumerate(hay):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                try:
                    obj = json.loads(hay[start: i + 1])
                except Exception:
                    continue
                if isinstance(obj, dict):
                    return obj
    return None


def chat(messages, temperature=0.2, timeout=120):
    """messages: list of {role, content}. Returns parsed JSON dict or {'answer': raw}."""
    r = _post("/api/chat", {
            "model": config.MODEL,
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
        }, timeout)
    content = r.json()["message"]["content"]
    parsed = _extract_json(content)
    if parsed is None:
        return {"thought": "model replied in plain text", "answer": content}
    return parsed


def ping():
    try:
        r = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        return r.ok
    except Exception:
        return False


def oneshot(system, user, temperature=0.2, timeout=120):
    """Single model call (no loop). For Scout plans and Sentinel verdicts."""
    r = _post("/api/chat", {
            "model": config.MODEL,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
        }, timeout)
    content = r.json()["message"]["content"]
    return _extract_json(content) or {"answer": content}


def chat_native(messages, tool_schemas, temperature=0.2, timeout=180):
    """One turn with NATIVE function calling (Ollama tools param).

    Returns (text, calls) where calls = [{"name", "args"}].
    File-sized payloads travel as real JSON types — no escaping roulette.
    """
    ollama_tools = [{"type": "function", "function": {
        "name": s["name"], "description": s.get("description", ""),
        "parameters": {"type": "object", "properties": s.get("args", {}),
                       "required": s.get("required", [])}}} for s in tool_schemas]
    r = _post("/api/chat",
        {"model": config.MODEL, "messages": messages, "tools": ollama_tools,
              "stream": False, "options": {"temperature": temperature}},
        timeout)
    msg = r.json()["message"]
    calls = [{"name": c["function"]["name"],
              "args": c["function"].get("arguments", {}) or {}}
             for c in (msg.get("tool_calls") or [])]
    return msg.get("content", "") or "", calls
