# session_id -> list of {"role": "user"/"assistant", "content": str}
_sessions: dict[str, list[dict]] = {}

MAX_HISTORY_TURNS = 5  # last N exchanges kept per session


def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def add_turn(session_id: str, role: str, content: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})
    # trim to last N turns (N user+assistant pairs = 2N entries)
    _sessions[session_id] = _sessions[session_id][-(MAX_HISTORY_TURNS * 2):]