from app.agent.memory.short_term import ShortTermMemory
from app.agent.memory.long_term import LongTermMemory
from app.agent.memory.entity_tracker import EntityTracker


class ContextManager:
    """上下文管理器：协调四层记忆"""

    def __init__(
        self,
        short_term: ShortTermMemory = None,
        long_term: LongTermMemory = None,
        entity_tracker: EntityTracker = None,
        max_tokens: int = 128000,
    ):
        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term or LongTermMemory()
        self.entity_tracker = entity_tracker or EntityTracker()
        self.max_tokens = max_tokens
        self.available_for_context = int(max_tokens * 0.8)

    async def build(
        self,
        session_id: str,
        user_input: str,
        scenario: str,
    ) -> str:
        parts = []

        short_term_messages = await self.short_term.get(session_id)
        if short_term_messages:
            parts.append(f"【最近对话】\n{self.short_term._format_conversation(short_term_messages)}")

        short_term_rounds = self._get_short_term_rounds(scenario)
        recent = short_term_messages[-short_term_rounds * 2:] if short_term_messages else []
        if recent:
            await self.short_term.add(session_id, "user", user_input)

        return "\n\n".join(parts) if parts else ""

    def _get_short_term_rounds(self, scenario: str) -> int:
        rounds_map = {
            "customer_service": 5,
            "operations": 3,
            "recommendation": 2,
        }
        return rounds_map.get(scenario, 3)