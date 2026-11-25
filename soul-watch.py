#!/usr/bin/env python3
"""S.O.U.L. auto-watch: Gmail -> tickets -> build, forever.

Loop (default every 5 min):
  1. intake.run_all()  — Gmail (+WA when live) -> OPEN tickets (deduped via seen.json)
  2. crew.run_queue()  — ONLY if new tickets filed (health-gated, budget fuse 25 calls)
  3. watchdog.check_once() — MAPE-K pass -> data/health.json

Safety baked in:
  - gmail_send / wa_send are CONFIRM_TOOLS: auto-mode builds but NEVER sends.
  - intake caps: max 10 mails, 5 tickets per run.
  - crew caps: 25 model calls per ticket, health-gated parallelism (0 on critical).
  - Logs to data/watch.log + systemd journal.

Env:
  SOUL_WATCH_INTERVAL  seconds between ticks (default 300)
  SOUL_WATCH_AUTOBUILD 1 = build new tickets, 0 = file only (default 1)

Usage:
  python3 soul-watch.py              # forever loop
  SOUL_WATCH_AUTOBUILD=0 python3 soul-watch.py   # safe mode: file only
"""
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import intake
import crew
import watchdog
import tickets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "data", "watch.log")

INTERVAL = int(os.getenv("SOUL_WATCH_INTERVAL", "300"))
AUTOBUILD = os.getenv("SOUL_WATCH_AUTOBUILD", "1") == "1"


def log(msg):
    line = f"[soul-watch {time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def tick_once():
    res = intake.run_all()
    created = res.get("created", [])
    if created:
        log(f"intake filed {len(created)}: {created}")
    else:
        log("intake: no new tasks")
    if AUTOBUILD:
        open_ids = [t["id"] for t in tickets.list_all("OPEN")]
        active = [t["id"] for t in tickets.list_all()
                  if t["status"] in ("PLANNED", "BUILDING", "REVIEWING")]
        if open_ids and not active:
            log(f"queue draining backlog: {open_ids}")
            done = crew.run_queue(open_ids)
            log(f"queue done: {done}")
        elif open_ids and active:
            log(f"queue busy (active={active}), {len(open_ids)} OPEN waiting")
    elif created:
        log("autobuild OFF: tickets left OPEN for manual approval")
    try:
        rep = watchdog.check_once()
        log(f"watchdog: open={rep['queue']['open']} active={rep['queue']['active']} "
            f"pressure={rep['pressure']} parallel={rep['recommended_parallel']}")
        if rep.get("actions"):
            log(f"watchdog actions: {rep['actions']}")
    except Exception as e:
        log(f"watchdog error: {e}")


def main():
    log(f"soul-watch online (interval={INTERVAL}s autobuild={'ON' if AUTOBUILD else 'OFF'})")
    while True:
        try:
            tick_once()
        except Exception:
            log("tick error:\n" + traceback.format_exc(limit=3))
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
