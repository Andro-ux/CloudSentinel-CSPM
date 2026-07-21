import time
from typing import Dict, Optional, Tuple
from backend.security.exceptions import RateLimitExceededError


class RateLimiter:
    def __init__(self):
        self._buckets: Dict[str, Dict[str, Any]] = {}

    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> Tuple[bool, Optional[int]]:
        now = time.time()
        bucket = self._buckets.get(key)
        if bucket is None:
            self._buckets[key] = {
                "count": 1,
                "window_start": now,
                "limit": limit,
                "window_seconds": window_seconds,
            }
            return True, None
        if now - bucket["window_start"] > window_seconds:
            bucket["count"] = 1
            bucket["window_start"] = now
            bucket["limit"] = limit
            bucket["window_seconds"] = window_seconds
            return True, None
        bucket["count"] += 1
        if bucket["count"] > limit:
            retry_after = int(window_seconds - (now - bucket["window_start"]))
            return False, max(retry_after, 1)
        return True, None

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        allowed, retry_after = self.is_allowed(key, limit, window_seconds)
        if not allowed:
            raise RateLimitExceededError(retry_after=retry_after)

    def clear(self) -> None:
        self._buckets.clear()
