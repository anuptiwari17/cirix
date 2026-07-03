import time

# session_id -> {"turns": [...], "last_used": timestamp}
_sessions: dict[str, dict] = {}

MAX_HISTORY_TURNS = 5       # last N exchanges kept per session
SESSION_TTL_SECONDS = 3600  # sessions unused for 1 hour get cleaned up


def _prune_expired_sessions():
    """Remove sessions that haven't been used in over SESSION_TTL_SECONDS."""
    now = time.time()
    expired = [
        sid for sid, data in _sessions.items()
        if now - data["last_used"] > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        del _sessions[sid]


def get_history(session_id: str) -> list[dict]:
    session = _sessions.get(session_id)
    return session["turns"] if session else []


def add_turn(session_id: str, role: str, content: str):
    _prune_expired_sessions()

    if session_id not in _sessions:
        _sessions[session_id] = {"turns": [], "last_used": time.time()}

    _sessions[session_id]["turns"].append({"role": role, "content": content})
    _sessions[session_id]["turns"] = _sessions[session_id]["turns"][-(MAX_HISTORY_TURNS * 2):]
    _sessions[session_id]["last_used"] = time.time()