"""Pure Python token bucket and a nonblocking work-concurrency gate."""
from __future__ import annotations

import math
import threading
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable


@dataclass
class Bucket:
    tokens: float
    updated_at: float


class TokenBucket:
    """Per-key token bucket. Concurrency safe inside one Python process only."""

    def __init__(self, capacity: int = 5, refill_per_second: float = 1,
                 clock: Callable[[],float] | None = None):
        if capacity <= 0 or refill_per_second <= 0:
            raise ValueError("Capacity and refill rate must be positive")
        self.capacity=capacity
        self.refill=refill_per_second
        self.clock=clock or time.monotonic
        self._buckets: dict[str,Bucket]={}
        self._lock=threading.Lock()

    def allow(self, key:str) -> tuple[bool,int]:
        with self._lock:
            now=self.clock()
            bucket=self._buckets.get(key)
            if bucket is None:
                bucket=Bucket(float(self.capacity),now)
                self._buckets[key]=bucket
            elapsed=max(0.0,now-bucket.updated_at)
            bucket.tokens=min(self.capacity,bucket.tokens+elapsed*self.refill)
            bucket.updated_at=now
            if bucket.tokens>=1.0:
                bucket.tokens-=1.0
                return True,0
            # Retry-After is a full number of seconds, always at least 1.
            wait=math.ceil((1.0-bucket.tokens)/self.refill)
            return False,max(1,wait)


class TrafficService:
    def __init__(self, capacity=5, refill_per_second=1.0, max_parallel=2,
                 clock:Callable[[],float] | None = None):
        if max_parallel <= 0: raise ValueError("max_parallel must be >0")
        self.limiter=TokenBucket(capacity,refill_per_second,clock)
        self._semaphore=threading.BoundedSemaphore(max_parallel)
        self._lock=threading.Lock()
        self._stats=Counter()
        self._active=0
        self._peak=0

    def process(self, client_key:str, work: Callable[[],object] | None = None):
        """Returns (status_code, result, retry_after) for easy API testing."""
        allowed,retry_after=self.limiter.allow(client_key)
        if not allowed:
            with self._lock:self._stats["rate_limited"]+=1
            return 429,{"error":"Rate limit exceeded"},retry_after
        if not self._semaphore.acquire(blocking=False):
            with self._lock:self._stats["over_capacity"]+=1
            return 503,{"error":"Worker capacity reached; retry later"},1
        try:
            with self._lock:
                self._active+=1
                self._peak=max(self._active,self._peak)
            try:
                result=work() if work else {"message":"Processed"}
            except Exception:
                with self._lock:self._stats["internal_error"]+=1
                raise
            with self._lock:self._stats["success"]+=1
            return 200,result,0
        finally:
            with self._lock:self._active-=1
            self._semaphore.release()

    def snapshot(self):
        with self._lock:
            return {"success":self._stats["success"],
                    "rate_limited":self._stats["rate_limited"],
                    "over_capacity":self._stats["over_capacity"],
                    "internal_error":self._stats["internal_error"],
                    "active":self._active,"peak_active":self._peak}
