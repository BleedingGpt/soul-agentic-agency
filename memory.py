"""S.O.U.L. memory — MemGPT-style two tiers + Generative-Agents-style scoring.

working  (RAM): last N turns of the live session, always in context.
archive (disk): data/memory.json — lessons + reflections, paged in by score.
score = relevance (term overlap) + recency (decay) + importance (heuristic).
"""
import json
import os
import re
import time
import config

MEM_PATH = os.path.join(config.DATA_DIR, "memory.json")
WORKING_N = 8


def _load():
    if os.path.exists(MEM_PATH):
        try:
            with open(MEM_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"lessons": [], "reflections": []}


def _save(db):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(MEM_PATH, "w") as f:
        json.dump(db, f, indent=2)


def _importance(text):
    t = text.lower()
    s = 1.0
    if any(k in t for k in ("fail", "error", "wrong", "lesson", "never", "always")):
        s += 2.0
    if any(k in t for k in ("send", "gmail", "whatsapp", "submit", "deadline")):
        s += 1.0
    return s


def remember(kind, text):
    """kind: 'lesson' | 'reflection'. Stored with timestamp + importance."""
    db = _load()
    db["lessons" if kind == "lesson" else "reflections"].append(
        {"text": text[: 500], "ts": time.time(), "importance": _importance(text)}
    )
    _save(db)


def recall(query, k=3):
    """Return top-k scored memories as context lines."""
    terms = set(re.findall(r"\w+", (query or "").lower()))
    db = _load()
    now = time.time()
    scored = []
    for kind in ("lessons", "reflections"):
        for m in db[kind]:
            words = set(re.findall(r"\w+", m["text"].lower()))
            relevance = len(terms & words)
            age_h = max((now - m["ts"]) / 3600.0, 0.01)
            recency = 1.0 / age_h
            score = relevance * 2.0 + min(recency, 5.0) * 0.3 + m.get("importance", 1.0)
            if relevance or m.get("importance", 0) >= 3.0:
                scored.append((score, f"[{kind}] {m['text']}"))
    scored.sort(reverse=True)
    return [t for _, t in scored[:k]]
