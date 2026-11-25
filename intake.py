"""S.O.U.L. Agency — intake clerks. Watch Gmail + WhatsApp, file OPEN tickets.

Gmail: search recent mail -> triage each via LLM (actionable task?) -> ticket.
WhatsApp: read recent chats -> triage message batches -> ticket.
Dedupe via data/seen.json (gmail IDs, message hashes). Caps keep it cheap:
max 10 mails, 3 chats x 5 msgs, 5 tickets per run.
"""
import hashlib
import json
import os
import re
import config
import llm
import tickets
import tools

SEEN_PATH = os.path.join(config.DATA_DIR, "seen.json")

TRIAGE_SYSTEM = """You are INTAKE CLERK for a ticket agency. Given a message, decide if it
contains an actionable task, request, deadline, or problem for the user.
Output EXACTLY ONE JSON object: {"task": true/false, "title": "<short task title>",
"description": "<who asked + what + any dates>"}. Greetings, reactions,
spam, and FYI-only messages are NOT tasks. English only."""


def _seen():
    if os.path.exists(SEEN_PATH):
        try:
            with open(SEEN_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"gmail": [], "wa": []}


def _save_seen(s):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    s["gmail"] = s["gmail"][-200:]
    s["wa"] = s["wa"][-200:]
    with open(SEEN_PATH, "w") as f:
        json.dump(s, f)


def _gmail_body(mid):
    """Fetch plain-text body for one Gmail ID. Returns '' on any failure
    (metadata-only triage still works, just dumber)."""
    try:
        import base64
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import config as _cfg
        tok = os.path.join(os.path.expanduser("~/bourbon/credentials"), "token.json")
        creds = Credentials.from_authorized_user_file(
            tok, ["https://www.googleapis.com/auth/gmail.readonly"])
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        svc = build("gmail", "v1", credentials=creds)

        def _walk(p):
            mt = p.get("mimeType", "")
            data = p.get("body", {}).get("data")
            if mt.startswith("text/plain") and data:
                try:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                except Exception:
                    return ""
            for q in p.get("parts", []):
                r = _walk(q)
                if r:
                    return r
            return ""

        m = svc.users().messages().get(userId="me", id=mid, format="full").execute()
        return _walk(m.get("payload", {}))[:2000]
    except Exception:
        return ""


def _triage(text):
    try:
        out = llm.oneshot(TRIAGE_SYSTEM, f"Message:\n{text[:1200]}")
        if out.get("task") is True and out.get("title"):
            return out["title"][: 120], out.get("description", "")[: 500]
    except Exception:
        pass
    return None


def gmail_scan(query="newer_than:2d", limit=10):
    """Returns list of created ticket ids."""
    seen, created = _seen(), []
    try:
        raw = tools.gmail_search(query)
    except Exception:
        return created
    blocks = re.split(r"\n\s*\n", raw)
    for b in blocks[:limit]:
        mid = re.search(r"ID:\s*(\S+)", b)
        if not mid:
            continue
        mid = mid.group(1)
        if mid in seen["gmail"] or len(created) >= 5:
            continue
        seen["gmail"].append(mid)
        body = _gmail_body(mid)
        snippet = f"\nBody:\n{body}" if body else ""
        t = _triage(b + snippet)
        if t:
            title, desc = t
            tickets.create(title, f"{desc}\n(source mail ID {mid})", source="gmail")
            created.append(title)
    _save_seen(seen)
    return created


def whatsapp_scan(max_chats=3, per_chat=5):
    seen, created = _seen(), []
    try:
        chats_raw = tools.wa_chats(10)
    except Exception:
        return created
    names = re.findall(r"\d+\.\s*(.+?)\s*\(\d+ unread\)", chats_raw)[:max_chats]
    if not names:  # fallback: numbered lines without unread counts
        names = [ln.strip("- ").strip() for ln in chats_raw.splitlines()
                 if ln.strip()][:max_chats]
    for name in names:
        try:
            msgs = tools.wa_read(name, per_chat)
        except Exception:
            continue
        h = hashlib.md5((name + msgs).encode()).hexdigest()
        if h in seen["wa"] or len(created) >= 5:
            continue
        seen["wa"].append(h)
        t = _triage(f"WhatsApp chat '{name}':\n{msgs}")
        if t:
            title, desc = t
            tickets.create(title, f"{desc}\n(from WhatsApp: {name})", source="whatsapp")
            created.append(title)
    _save_seen(seen)
    return created


def run_all():
    g = gmail_scan()
    w = whatsapp_scan()
    return {"created": g + w, "gmail": len(g), "whatsapp": len(w)}
