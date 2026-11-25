# S.O.U.L. - Agentic Ticket Agency

A multi-agent system that takes a real task, turns it into a ticket, and ships it with guardrails. Built as a solo course project for Mondira's AI-Theory class in September 2026.

## Why

Most "agent demo" projects are a chat loop with a tool attached. This one has a queue, role separation, a call budget, a send gate, and a watchdog, because an agent that can send email needs more than a prompt.

## How it works

Intake clerks file tickets into `data/tickets.json`. A dispatcher assigns each ticket to Scout (plan), Builder (implement), and Sentinel (verify). A watchdog watches for stalls, and a 25-call fuse stops runaway model usage. External actions pass through a send gate.

Architecture and ReAct loop diagrams are in `docs/soul-architecture.mmd` and `docs/soul-react-loop.mmd` (rendered PNGs alongside).

## Receipts

- 5 tickets shipped end-to-end: password generator CLI, CSV to JSON, todo CLI, a single-page site, and a dice roller.
- 25-call budget fuse caught a real runaway (T-002 burned 26 calls) and stopped the bleed.
- 300-second watchdog for unattended runs; 15-second and 5-second demo ticks.
- Fresh evaluation: 2 of 4 tickets passed. Portfolio-class tickets correctly FAILED instead of being faked. The failures are kept in `data/tickets.json` as evidence.
- Live demo on 29 Sep 2026: a real Gmail task was driven to DONE in front of the class.
- Skill auto-learning was proven by ticket T-005; learned skills are in `skills/auto-t-*`.

## Stack

Python, FastAPI, Uvicorn, Ollama (`gpt-oss:120b-cloud` primary, `llama3.2:3b` offline fallback), Gmail API, systemd.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open `http://localhost:8000` for the board. `soul-watch.py` is the systemd watcher entry point; set `SOUL_WATCH_INTERVAL=15` for a fast demo.

## Honest limitations

This is a course demo, not a production service. Two fresh tickets failed. The cloud brain is swapped by environment variable, not by a config UI. There is no authentication on the local board, so do not expose port 8000 publicly.

## Privacy

No API keys or personal credentials are committed. The original intake email address has been replaced with `user@example.com` in the ticket history.

## Author

Ishtiaq Ahmed, Department of CSE, Notre Dame University Bangladesh. Course report: `ID_35_SOUL_Agent_Report.pdf`.
