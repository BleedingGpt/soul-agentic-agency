"""S.O.U.L. server — FastAPI. One port, shippable anywhere. Run: python3 app.py"""
import os
import subprocess
import threading
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import config
import agent
import crew
import intake
import llm
import tickets
import watchdog

app = FastAPI(title="S.O.U.L.")
app.mount("/static", StaticFiles(directory=os.path.join(config.BASE_DIR, "static")), name="static")


class ChatIn(BaseModel):
    message: str


class DecideIn(BaseModel):
    id: str
    approve: bool


class TicketIn(BaseModel):
    title: str
    description: str = ""
    source: str = "manual"


@app.get("/")
def index():
    return FileResponse(os.path.join(config.BASE_DIR, "static", "index.html"))


@app.get("/board")
def board():
    return FileResponse(os.path.join(config.BASE_DIR, "static", "board.html"))


@app.get("/report/agent-proposal.html")
def proposal():
    return FileResponse(os.path.join(config.BASE_DIR, "report", "agent-proposal.html"))


@app.get("/api/health")
def health():
    wa = subprocess.run([config.WA_CLI, "status"], capture_output=True, text=True, timeout=8)
    return {"model": config.MODEL, "ollama": llm.ping(),
            "whatsapp": (wa.stdout or "")[: 300],
            "gmail_script": os.path.exists(config.GMAIL_SCRIPT)}


@app.post("/api/chat")
def chat(inp: ChatIn):
    msg = (inp.message or "").strip()
    if not msg:
        return {"status": "error", "answer": "Empty message.", "trace": []}
    return agent.run(msg)


@app.post("/api/decide")
def decide(inp: DecideIn):
    return agent.resume(inp.id, inp.approve)


@app.get("/api/tickets")
def tickets_list():
    return tickets.list_all()


@app.post("/api/tickets")
def ticket_create(inp: TicketIn):
    return tickets.create(inp.title, inp.description, inp.source)


@app.post("/api/tickets/run")
def tickets_run():
    """Dispatch all OPEN tickets through the adaptive queue (background)."""
    ids = [t["id"] for t in tickets.list_all("OPEN")]
    threading.Thread(target=crew.run_queue, args=(ids,), daemon=True).start()
    return {"accepted": ids}


@app.get("/api/health-full")
def health_full():
    return watchdog.check_once()


@app.post("/api/intake/run")
def intake_run():
    return intake.run_all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("SOUL_PORT", "8000")))
