from typing import Optional


class EntityTracker:
    """实体槽位追踪"""

    def __init__(self):
        self._slots: dict[str, dict] = {}

    def update(self, session_id: str, extracted: dict):
        if session_id not in self._slots:
            self._slots[session_id] = {
                "cards": [],
                "transactions": [],
                "recent_entity": None,
                "user_profile": {},
            }
        self._slots[session_id].update(extracted)

    def get(self, session_id: str) -> dict:
        return self._slots.get(session_id, {
            "cards": [],
            "transactions": [],
            "recent_entity": None,
            "user_profile": {},
        })

    def resolve_reference(self, session_id: str, reference: str, entity_type: str) -> Optional[str]:
        slots = self.get(session_id)
        if reference in ["那张卡", "那张", "刚才的卡"]:
            cards = slots.get("cards", [])
            return cards[0] if cards else None
        elif reference in ["刚才那笔", "刚才的消费"]:
            txns = slots.get("transactions", [])
            return txns[0] if txns else None
        return None

    def clear(self, session_id: str):
        if session_id in self._slots:
            del self._slots[session_id]