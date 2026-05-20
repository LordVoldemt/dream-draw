from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone


class IpRateLimiter:
    def __init__(self, max_requests: int = 5, window_minutes: int = 1) -> None:
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self._entries: dict[str, deque[datetime]] = {}

    def allow(self, ip_address: str) -> bool:
        now = datetime.now(timezone.utc)
        queue = self._entries.setdefault(ip_address, deque())
        while queue and now - queue[0] > self.window:
            queue.popleft()
        if len(queue) >= self.max_requests:
            return False
        queue.append(now)
        return True


ip_rate_limiter = IpRateLimiter()
