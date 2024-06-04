"""One-process token bucket, not a distributed quota system."""
import math
import threading
import time
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

class TokenBuckets:
    def __init__(self, capacity=3, refill_per_second=1.0, clock=None):
        if capacity <= 0 or refill_per_second <= 0:
            raise ValueError('Capacity/refill must be positive')
        self.capacity = capacity
        self.refill = refill_per_second
        self.clock = clock or time.monotonic
        self.buckets = {}
        self.lock = threading.Lock()

    def consume(self, client_id):
        with self.lock:
            now = self.clock()
            tokens, last = self.buckets.get(client_id, (float(self.capacity), now))
            tokens = min(self.capacity, tokens + max(0, now - last) * self.refill)
            if tokens < 1:
                self.buckets[client_id] = (tokens, now)
                return False, 0, max(1, math.ceil((1.0-tokens)/self.refill))
            tokens -= 1
            self.buckets[client_id] = (tokens, now)
            return True, int(tokens), 0

def create_app(clock=None, keys=None, capacity=3, refill_per_second=1.0):
    api = FastAPI(title='Token Bucket Rate Limiter')
    keys = keys or {'demo-alpha', 'demo-beta'}
    limiter = TokenBuckets(capacity, refill_per_second, clock)

    @api.get('/reports')
    def reports(x_api_key: str = Header(default='')):
        if x_api_key not in keys:
            raise HTTPException(401, 'Unknown API key')
        allowed, remaining, retry_seconds = limiter.consume(x_api_key)
        if not allowed:
            return JSONResponse(status_code=429, content={'detail':'Rate limit exceeded'},
                                headers={'Retry-After':str(retry_seconds), 'X-RateLimit-Remaining':'0'})
        return JSONResponse({'report':'Example sales report','total_cents':1799},
                            headers={'X-RateLimit-Remaining':str(remaining)})

    return api

app = create_app()
