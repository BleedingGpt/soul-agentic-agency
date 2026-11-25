"""Per-ticket model-call budget. Thread-local: each dispatcher worker thread
gets its own counter. No active ticket -> tick() is a no-op (S.O.U.L. chat
and crew oneshots are unaffected)."""


class BudgetExceeded(Exception):
    pass


import threading as _th
_state = _th.local()


def start(max_calls=25):
    _state.active = True
    _state.used = 0
    _state.max = max_calls


def tick():
    if not getattr(_state, "active", False):
        return 0
    _state.used += 1
    if _state.used > _state.max:
        raise BudgetExceeded(f"ticket used {_state.used} model calls (cap {_state.max})")
    return _state.used


def usage():
    return getattr(_state, "used", 0)


def end():
    used = getattr(_state, "used", 0)
    _state.active = False
    return used
