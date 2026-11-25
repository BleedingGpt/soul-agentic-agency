"""S.O.U.L. Agency — ticket store. JSON file: transparent, demo-friendly.

Lifecycle (orchestrator-enforced, code-driven — never agent free-chat):
  OPEN -> PLANNED -> BUILDING -> REVIEWING -> DONE
                        |            |
                        |            +--FAIL notes--> BUILDING (max 2 retries)
                        +---------------------------> FAILED
"""
import json
import os
import threading
import time
import config

TICKETS_PATH = os.path.join(config.DATA_DIR, "tickets.json")
_LOCK = threading.Lock()  # parallel dispatcher workers share this process

STATUSES = ["OPEN", "PLANNED", "BUILDING", "REVIEWING", "DONE", "FAILED"]


def _load():
    if os.path.exists(TICKETS_PATH):
        try:
            with open(TICKETS_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"seq": 0, "tickets": {}}


def _save(db):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(TICKETS_PATH, "w") as f:
        json.dump(db, f, indent=2)


def _now():
    return time.strftime("%Y-%m-%d %H:%M")


def create(title, description="", source="manual"):
    with _LOCK:
        db = _load()
        db["seq"] += 1
        tid = f"T-{db['seq']:03d}"
        db["tickets"][tid] = {
            "id": tid, "title": title, "description": description, "source": source,
            "status": "OPEN", "created": _now(), "updated": _now(),
            "history": [f"created from {source}"], "artifacts": {}, "retries": 0,
        }
        _save(db)
        return db["tickets"][tid]


def get(tid):
    return _load()["tickets"].get(tid)


def list_all(status=None):
    ts = _load()["tickets"].values()
    if status:
        ts = [t for t in ts if t["status"] == status]
    return sorted(ts, key=lambda t: t["id"])


def transition(tid, status, note="", artifacts=None):
    with _LOCK:
        db = _load()
        t = db["tickets"].get(tid)
        if not t or status not in STATUSES:
            return None
        t["status"] = status
        t["updated"] = _now()
        t["history"].append(f"-> {status}: {note}" if note else f"-> {status}")
        if artifacts:
            t["artifacts"].update(artifacts)
        _save(db)
        return t


def note(tid, text):
    with _LOCK:
        db = _load()
        t = db["tickets"].get(tid)
        if t:
            t["history"].append(text)
            t["updated"] = _now()
            _save(db)
        return t


def set_artifact(tid, key, value):
    with _LOCK:
        db = _load()
        t = db["tickets"].get(tid)
        if t:
            t["artifacts"][key] = value
            t["updated"] = _now()
            _save(db)
        return t
