import redis.asyncio as redis
import json
from typing import Optional

class SemanticCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = await redis.from_url(self.redis_url)
        return self._client

    async def get(self, key: str) -> Optional[dict]:
        client = await self.get_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: dict, ttl: int = 3600):
        client = await self.get_client()
        await client.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str):
        client = await self.get_client()
        await client.delete(key)

    async def clear_all(self):
        client = await self.get_client()
        await client.flushdb()

    async def get_stats(self) -> dict:
        client = await self.get_client()
        info = await client.info("stats")
        return {
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }