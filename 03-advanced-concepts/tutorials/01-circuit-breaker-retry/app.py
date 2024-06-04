"""A circuit-breaker and bounded retry demo with a fake supplier."""
import threading
import time
from fastapi import FastAPI, HTTPException

class SupplierUnavailable(Exception):
    pass

class FakeSupplier:
    def __init__(self, failures_left=0):
        self.failures_left = failures_left
        self.calls = 0

    def fetch(self, sku):
        self.calls += 1
        if self.failures_left:
            self.failures_left -= 1
            raise SupplierUnavailable('Supplier request failed')
        return {'sku': sku, 'price_cents': 2499}

class CircuitBreaker:
    def __init__(self, threshold=2, cooldown=10.0, clock=None):
        self.threshold = threshold
        self.cooldown = cooldown
        self.clock = clock or time.monotonic
        self.failures = 0
        self.opened_at = None
        self.probe_in_flight = False
        self.lock = threading.Lock()

    def allow(self):
        with self.lock:
            if self.opened_at is None:
                return True
            if self.clock() - self.opened_at < self.cooldown:
                return False
            if self.probe_in_flight:
                return False
            self.probe_in_flight = True
            return True

    def success(self):
        with self.lock:
            self.failures = 0
            self.opened_at = None
            self.probe_in_flight = False

    def failure(self):
        with self.lock:
            self.probe_in_flight = False
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = self.clock()

    def status(self):
        with self.lock:
            if self.opened_at is None:
                return 'closed'
            if self.clock() - self.opened_at >= self.cooldown:
                return 'half-open'
            return 'open'

def create_app(supplier=None, clock=None, threshold=2, cooldown=10):
    api = FastAPI(title='Circuit Breaker Experiment')
    supplier = supplier or FakeSupplier()
    breaker = CircuitBreaker(threshold=threshold, cooldown=cooldown, clock=clock)
    api.state.supplier = supplier
    api.state.breaker = breaker

    @api.get('/quotes/{sku}')
    def get_quote(sku: str):
        if not breaker.allow():
            raise HTTPException(503, 'Supplier circuit open; retry later')
        # One retry, with no real sleep for this deterministic lab.
        for attempt in range(2):
            try:
                quote = supplier.fetch(sku)
                breaker.success()
                return quote
            except SupplierUnavailable:
                if attempt == 1:
                    breaker.failure()
                    raise HTTPException(503, 'Supplier could not return a quote')

    @api.get('/health/supplier')
    def health():
        return {'circuit': breaker.status(), 'calls': supplier.calls}

    return api

app = create_app()
