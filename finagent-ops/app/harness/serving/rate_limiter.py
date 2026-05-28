import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._buckets = defaultdict(lambda: {"tokens": requests_per_minute, "last_refill": time.time()})

    def check_limit(self, key: str) -> bool:
        bucket = self._buckets[key]
        now = time.time()

        if now - bucket["last_refill"] >= 60:
            bucket["tokens"] = self.requests_per_minute
            bucket["last_refill"] = now

        if bucket["tokens"] > 0:
            bucket["tokens"] -= 1
            return True
        return False

    def get_remaining(self, key: str) -> int:
        bucket = self._buckets[key]
        return max(0, bucket["tokens"])