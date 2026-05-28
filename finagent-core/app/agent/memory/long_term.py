from typing import Optional


class LongTermMemory:
    """长期记忆（用户画像）"""

    def __init__(self):
        self._profiles: dict[str, dict] = {}

    async def get_profile(self, user_id: str) -> dict:
        return self._profiles.get(user_id, {})

    async def update_profile(self, user_id: str, updates: dict):
        if user_id not in self._profiles:
            self._profiles[user_id] = {}
        self._profiles[user_id].update(updates)

    async def add_interaction(self, user_id: str, interaction: dict):
        if user_id not in self._profiles:
            self._profiles[user_id] = {"interactions": []}
        if "interactions" not in self._profiles[user_id]:
            self._profiles[user_id]["interactions"] = []
        self._profiles[user_id]["interactions"].append(interaction)

    async def search_memories(self, user_id: str, query: str) -> list[dict]:
        profile = await self.get_profile(user_id)
        interactions = profile.get("interactions", [])
        return [i for i in interactions if query.lower() in str(i).lower()]