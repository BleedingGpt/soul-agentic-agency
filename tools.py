"""S.O.U.L. tools — Toolformer-style registry. Every tool: text in, text out."""
import os
import re
import subprocess
import config

VAULT_SEARCH_DIRS = ["concepts", "labs", "memory", "insights", "context", "user-profile"]


def _run(cmd, timeout=None):
    p = subprocess.run(cmd, capture_output=True, text=True,
                       timeout=timeout or config.TOOL_TIMEOUT)
    out = (p.stdout or "") + (p.stderr or "")
    return out.strip()[: config.MAX_OBS_CHARS] or "(empty result)"


# ---- Gmail (wraps ~/bourbon/scripts/gmail-search.py) ----
def gmail_search(query):
    return _run(["python3", config.GMAIL_SCRIPT, query])


def gmail_send(to, subject, body):
    return _run(["python3", config.GMAIL_SCRIPT, "--send", to, subject, body])


# ---- WhatsApp (wraps ~/bourbon/scripts/wa -> daemon :3008) ----
def wa_chats(limit=8):
    return _run([config.WA_CLI, "chats", str(limit)])


def wa_read(chat, limit=10):
    return _run([config.WA_CLI, "read", chat, str(limit)])


def wa_send(to, text):
    return _run([config.WA_CLI, "send", to, text])


# ---- Calculator (sandboxed: digits + operators only, never bare eval) ----
def calculator(expression):
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expression or ""):
        return "Error: only digits and + - * / ( ) . allowed."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"


# ---- Notes search (v1: scored keyword scan over the vault; upgrade path: rag.py) ----
def notes_search(query, per_file=2, max_files=4):
    terms = [t.lower() for t in re.findall(r"\w+", query or "") if len(t) > 2]
    if not terms:
        return "Error: empty query."
    hits = []
    for sub in VAULT_SEARCH_DIRS:
        d = os.path.join(config.VAULT_DIR, sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith(".md"):
                continue
            fp = os.path.join(d, fn)
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()
            except Exception:
                continue
            scored = []
            for i, ln in enumerate(lines):
                low = ln.lower()
                s = sum(low.count(t) for t in terms)
                if s:
                    scored.append((s, i, ln.strip()[: 220]))
            if scored:
                scored.sort(reverse=True)
                best = scored[:per_file]
                score = sum(s for s, _, _ in best)
                hits.append((score, f"{sub}/{fn}", [ln for _, _, ln in best]))
    if not hits:
        return "No matching notes found."
    hits.sort(reverse=True)
    out = []
    for score, name, lines in hits[:max_files]:
        out.append(f"[{name} score={score}]")
        out += [f"  - {ln}" for ln in lines]
    return "\n".join(out)[: config.MAX_OBS_CHARS]


# ---- Save note (agent WRITES to the world: vault fleeting file, timestamped) ----
def save_note(text, title="soul-note"):
    import time as _t
    d = os.path.join(config.VAULT_DIR, "fleeting")
    os.makedirs(d, exist_ok=True)
    safe = re.sub(r"[^a-z0-9-]+", "-", (title or "soul-note").lower()).strip("-") or "soul-note"
    fp = os.path.join(d, f"{safe}.md")
    entry = f"\n\n## S.O.U.L. — {_t.strftime('%Y-%m-%d %H:%M')}\n{text.strip()}\n"
    try:
        with open(fp, "a", encoding="utf-8") as f:
            f.write(entry)
        return f"Saved to fleeting/{safe}.md"
    except Exception as e:
        return f"Error saving note: {e}"


# ---- Web fetch (agent READS the internet: URL -> plain text, capped) ----
def web_fetch(url, max_chars=3000):
    try:
        import urllib.request
        req = urllib.request.Request((url or "").strip(),
                                     headers={"User-Agent": "Mozilla/5.0 (S.O.U.L. student agent)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read(60000).decode("utf-8", errors="ignore")
        text = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "…[truncated]"
        return text or "(page had no readable text)"
    except Exception as e:
        return f"Error fetching page: {e}"


# ---- Remember (agent LEARNS: writes its own long-term memory) ----
def remember(text, kind="lesson"):
    try:
        import memory as _mem
        kind = kind if kind in ("lesson", "reflection") else "lesson"
        _mem.remember(kind, text)
        return f"Remembered as {kind}."
    except Exception as e:
        return f"Error remembering: {e}"


# ---- Workspace (Builder sandbox: reads/writes confined to workspace/) ----
WORKSPACE = os.path.join(config.BASE_DIR, "workspace")


def _safe_path(name):
    """Confine to WORKSPACE. Rejects absolute paths and '..' escapes.
    Strips a leading 'workspace/' so agents can't double-nest it."""
    name = (name or "").lstrip("/")
    while name.startswith("workspace/"):
        name = name[len("workspace/"):]
    base = os.path.abspath(WORKSPACE)
    fp = os.path.abspath(os.path.join(base, name))
    if fp != base and not fp.startswith(base + os.sep):
        return None
    return fp


def workspace_write(path, content):
    fp = _safe_path(path)
    if not fp:
        return "Error: path escapes the workspace. Stay inside workspace/."
    try:
        os.makedirs(os.path.dirname(fp) or WORKSPACE, exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content or "")
        return f"Wrote {path} ({len(content or '')} chars)."
    except Exception as e:
        return f"Error writing file: {e}"


def workspace_read(path):
    fp = _safe_path(path)
    if not fp or not os.path.isfile(fp):
        return f"Error: '{path}' not found in workspace."
    try:
        with open(fp, encoding="utf-8", errors="ignore") as f:
            data = f.read()
        return data[: 4000] + ("…[truncated]" if len(data) > 4000 else "")
    except Exception as e:
        return f"Error reading file: {e}"


def workspace_list(prefix=""):
    out = []
    for root, _, files in os.walk(WORKSPACE):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if fn.endswith(".pyc"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, WORKSPACE)
            if rel.startswith(prefix or ""):
                out.append(f"{rel} ({os.path.getsize(full)}B)")
    return "\n".join(out) or "(workspace empty)"


# ---- Code check (Sentinel's deterministic checks: syntax + secrets + hygiene) ----
_SECRET_RES = ["api[_-]?key", "sk-[a-z0-9]{8,}", "ghp_[a-z0-9]+", "nvapi-[a-z0-9-]+",
               "password\\s*=", "secret\\s*="]


def code_check(path_prefix=""):
    import py_compile
    report = []
    base = os.path.abspath(WORKSPACE)
    targets = []
    for root, _, files in os.walk(base):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if fn.endswith(".pyc"):
                continue
            rel = os.path.relpath(os.path.join(root, fn), base)
            if rel.startswith(path_prefix or ""):
                targets.append((rel, os.path.join(root, fn)))
    if not targets:
        return "FAIL: no files found to check."
    for rel, fp in targets:
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                src = f.read()
        except Exception as e:
            report.append(f"[READ-FAIL] {rel}: {e}")
            continue
        if rel.endswith(".py"):
            try:
                py_compile.compile(fp, doraise=True)
                report.append(f"[OK] {rel}: python syntax clean")
            except Exception as e:
                report.append(f"[SYNTAX-FAIL] {rel}: {e}")
        if rel.endswith(".js"):
            p = subprocess.run(["node", "--check", fp], capture_output=True, text=True, timeout=15)
            report.append(f"[{'OK' if p.returncode == 0 else 'SYNTAX-FAIL'}] {rel}: node --check"
                          + ("" if p.returncode == 0 else f" {p.stderr.strip()[:200]}"))
        if rel.endswith((".html", ".css")) and len(src.strip()) > 0:
            report.append(f"[OK] {rel}: present ({len(src)} chars)")
        low = src.lower()
        for pat in _SECRET_RES:
            if re.search(pat, low):
                report.append(f"[SECRET-WARN] {rel}: possible embedded secret matching '{pat}'")
        # Placeholders live in comments, not in domain words: a todo APP will
        # legitimately say "todo" everywhere. Flag TODO/FIXME only in comments.
        if rel.endswith((".py", ".js")):
            comments = "\n".join(ln for ln in src.splitlines() if "#" in ln or "//" in ln)
            if re.search(r"\btodo\b|\bfixme\b", comments.lower()):
                report.append(f"[HYGIENE] {rel}: TODO/FIXME placeholder left in comments")
        if "lorem ipsum" in low:
            report.append(f"[HYGIENE] {rel}: lorem ipsum filler text")
    fails = sum(1 for r in report if "FAIL" in r)
    verdict = "FAIL" if fails else "PASS"
    return f"{verdict}: {len(targets)} file(s), {fails} hard failure(s)\n" + "\n".join(report)


TOOLS = {
    "gmail_search": lambda a: gmail_search(a.get("query", "")),
    "gmail_send": lambda a: gmail_send(a.get("to", ""), a.get("subject", ""), a.get("body", "")),
    "wa_chats": lambda a: wa_chats(a.get("limit", 8)),
    "wa_read": lambda a: wa_read(a.get("chat", ""), a.get("limit", 10)),
    "wa_send": lambda a: wa_send(a.get("to", ""), a.get("text", "")),
    "calculator": lambda a: calculator(a.get("expression", "")),
    "notes_search": lambda a: notes_search(a.get("query", "")),
    "save_note": lambda a: save_note(a.get("text", ""), a.get("title", "soul-note")),
    "web_fetch": lambda a: web_fetch(a.get("url", "")),
    "remember": lambda a: remember(a.get("text", ""), a.get("kind", "lesson")),
    "workspace_write": lambda a: workspace_write(a.get("path", ""), a.get("content", "")),
    "workspace_read": lambda a: workspace_read(a.get("path", "")),
    "workspace_list": lambda a: workspace_list(a.get("prefix", "")),
    "code_check": lambda a: code_check(a.get("path_prefix", "")),
}

DESCRIBE = {
    "gmail_search": "Search Gmail inbox",
    "gmail_send": "SEND an email (needs approval)",
    "wa_chats": "List recent WhatsApp chats",
    "wa_read": "Read a WhatsApp chat",
    "wa_send": "SEND a WhatsApp message (needs approval)",
    "calculator": "Evaluate arithmetic",
    "notes_search": "Search personal study notes",
    "save_note": "WRITE a timestamped note into the vault",
    "web_fetch": "Read a web page as plain text",
    "remember": "Store a lesson/reflection in long-term memory",
    "workspace_write": "WRITE a file inside workspace/ (sandboxed)",
    "workspace_read": "READ a file inside workspace/",
    "workspace_list": "LIST files inside workspace/",
    "code_check": "RUN syntax + secrets + hygiene checks on workspace files",
}
