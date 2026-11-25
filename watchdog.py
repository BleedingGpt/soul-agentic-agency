"""S.O.U.L. Agency — Watchdog. A MAPE-K self-healing loop for the agency itself.

  Monitor : PC load (health.py) + queue depth + stuck tickets + Ollama/WA/Gmail
  Analyze : pressure score, stuck = active ticket untouched >30 min, dead services
  Plan    : recommended parallelism, action list
  Execute : write data/health.json, flag stuck tickets, log (future: WA alert)
  Knowledge: tickets.json + health.json
"""
import json
import os
import subprocess
import time
import config
import health
import llm
import tickets

HEALTH_PATH = os.path.join(config.DATA_DIR, "health.json")
STUCK_MIN = 30


def _svc():
    out = {"ollama": llm.ping(), "whatsapp": "unknown", "gmail_script": os.path.exists(config.GMAIL_SCRIPT)}
    try:
        p = subprocess.run([config.WA_CLI, "status"], capture_output=True, text=True, timeout=8)
        out["whatsapp"] = "connected" if '"connected": true' in (p.stdout or "") else "down"
    except Exception:
        out["whatsapp"] = "down"
    return out


def _stuck():
    now = time.time()
    found = []
    for t in tickets.list_all():
        if t["status"] in ("BUILDING", "REVIEWING", "PLANNED"):
            try:
                age = (now - time.mktime(time.strptime(t.get("updated", t["created"]), "%Y-%m-%d %H:%M"))) / 60
            except Exception:
                age = 0
            if age > STUCK_MIN:
                found.append(t["id"])
    return found


def check_once():
    """One MAPE-K pass. Returns the report dict and persists it."""
    snap = health.snapshot()
    pressure = health.score(snap)
    open_n = len(tickets.list_all("OPEN"))
    active = [t["id"] for t in tickets.list_all()
              if t["status"] in ("PLANNED", "BUILDING", "REVIEWING")]
    stuck = _stuck()
    svcs = _svc()
    actions = []
    for tid in stuck:
        tickets.note(tid, "watchdog: flagged STUCK (no progress 30m+) — needs human or re-run")
        actions.append(f"flagged {tid} stuck")
    if svcs["whatsapp"] == "down":
        actions.append("whatsapp daemon down — needs `wa pair`")
    report = {"ts": time.strftime("%Y-%m-%d %H:%M"), "pressure": pressure,
              "snapshot": snap, "recommended_parallel": health.advice(snap),
              "queue": {"open": open_n, "active": active, "stuck": stuck},
              "services": svcs, "actions": actions}
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(HEALTH_PATH, "w") as f:
        json.dump(report, f, indent=2)
    return report


def run_forever(interval=120):
    while True:
        try:
            check_once()
        except Exception:
            pass
        time.sleep(interval)
