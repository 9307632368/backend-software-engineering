from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest
from fastapi.testclient import TestClient
from traffic_spike.app import create_app
from traffic_spike.service import TokenBucket,TrafficService


class Clock:
    def __init__(self):self.now=0.0
    def __call__(self):return self.now
    def advance(self,seconds):self.now+=seconds


@pytest.fixture
def api():
    clock=Clock()
    service=TrafficService(capacity=3,refill_per_second=1,max_parallel=2,clock=clock)
    return TestClient(create_app(service=service,work_delay=0)),clock


def test_three_request_burst_then_429(api):
    client,_=api
    headers={"X-Client-Key":"student"}
    assert [client.get("/work",headers=headers).status_code for _ in range(3)]==[200,200,200]
    last=client.get("/work",headers=headers)
    assert last.status_code==429
    assert last.headers["Retry-After"]=="1"


def test_bucket_refill_allows_later_request(api):
    client,clock=api
    for _ in range(3):client.get("/work",headers={"X-Client-Key":"alice"})
    assert client.get("/work",headers={"X-Client-Key":"alice"}).status_code==429
    clock.advance(1)
    assert client.get("/work",headers={"X-Client-Key":"alice"}).status_code==200


def test_clients_have_separate_buckets(api):
    client,_=api
    for _ in range(3):client.get("/work",headers={"X-Client-Key":"alice"})
    assert client.get("/work",headers={"X-Client-Key":"bob"}).status_code==200


def test_health_remains_responsive(api):
    client,_=api
    assert client.get("/health").json()=={"status":"ok"}


def test_metrics_count_rejections(api):
    client,_=api
    for _ in range(5):client.get("/work",headers={"X-Client-Key":"a"})
    stats=client.get("/metrics").json()
    assert stats["success"]==3
    assert stats["rate_limited"]==2
    assert stats["active"]==0


def test_nonblocking_bulkhead_returns_503():
    service=TrafficService(capacity=20,refill_per_second=1,max_parallel=1)
    entered=Event();release=Event()
    def hold():
        entered.set()
        release.wait(timeout=3)
        return {"done":True}
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(service.process,"buyer-1",hold)
        assert entered.wait(timeout=3)
        code,data,wait=service.process("buyer-2",lambda:{"done":True})
        assert code==503
        assert wait==1
        release.set()
        assert first.result(timeout=3)[0]==200
    assert service.snapshot()["peak_active"]==1
    assert service.snapshot()["over_capacity"]==1


def test_bucket_validation():
    with pytest.raises(ValueError):TokenBucket(capacity=0)
    with pytest.raises(ValueError):TrafficService(max_parallel=0)


def test_backward_clock_does_not_generate_tokens():
    clock=Clock();bucket=TokenBucket(capacity=1,clock=clock)
    assert bucket.allow("x")[0]
    clock.now=-100
    assert not bucket.allow("x")[0]


def test_unknown_identity_is_grouped_as_anonymous(api):
    client,_=api
    assert client.get("/work").status_code==200
    assert client.get("/work").status_code==200
    assert client.get("/work").status_code==200
    assert client.get("/work").status_code==429
