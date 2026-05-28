from datetime import datetime


class ShortTermMemory:
    """短期记忆（会话级）"""

    def __init__(self, max_rounds: int = 5, ttl_hours: int = 24):
        self.max_rounds = max_rounds
        self.ttl_hours = ttl_hours
        self._sessions: dict[str, list[dict]] = {}

    async def add(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

        if len(self._sessions[session_id]) > self.max_rounds * 2:
            self._sessions[session_id] = self._sessions[session_id][-self.max_rounds * 2:]

    async def get(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    async def clear(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _format_conversation(self, messages: list[dict]) -> str:
        if not messages:
            return ""
        lines = []
        for msg in messages:
            role = "用户" if msg["role"] == "user" else "助手"
            lines.append(f"{role}：{msg['content']}")
        return "\n".join(lines)