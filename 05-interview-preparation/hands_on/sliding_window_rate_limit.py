"""Interview practice 02: a per-key sliding-window rate limiter."""
import math
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Callable

from fastapi import FastAPI, Header, HTTPException


class SlidingWindowLimiter:
    def __init__(self, capacity: int = 3, seconds: float = 60, clock: Callable[[], float] = time.monotonic):
        if capacity <= 0 or seconds <= 0:
            raise ValueError('capacity and seconds must be positive')
        self.capacity, self.seconds, self.clock = capacity, seconds, clock
        self.events = defaultdict(deque)
        self.lock = Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        with self.lock:
            now = self.clock()
            q = self.events[key]
            while q and q[0] <= now - self.seconds:
                q.popleft()
            if len(q) >= self.capacity:
                return False, max(1, math.ceil(q[0] + self.seconds - now))
            q.append(now)
            return True, 0


def create_app(limiter: SlidingWindowLimiter | None = None) -> FastAPI:
    app = FastAPI(title='Interview 02 - In-memory Rate Limiting')
    limiter = limiter or SlidingWindowLimiter()

    @app.get('/search')
    def search(q: str, x_api_key: str = Header(min_length=1)):
        allowed, retry_after = limiter.allow(x_api_key)
        if not allowed:
            raise HTTPException(429, 'Too many requests', headers={'Retry-After': str(retry_after)})
        return {'query': q, 'results': []}

    return app


app = create_app()
