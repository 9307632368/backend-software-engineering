from fastapi.testclient import TestClient
from app import create_app

def test_submit_claim_complete(tmp_path):
    c=TestClient(create_app(tmp_path/'jobs.db'))
    j=c.post('/jobs',json={'task':'send-receipt','data':'order-12'}).json()['id']
    claim=c.post('/worker/claim').json()['job']
    assert claim['id']==j and claim['attempts']==1
    assert c.post(f'/worker/{j}/complete',json={'lease_token':'wrong'}).status_code==409
    assert c.post(f'/worker/{j}/complete',json={'lease_token':claim['lease_token']}).json()['status']=='done'
    assert c.get(f'/jobs/{j}').json()['status']=='done'
    assert c.post('/worker/claim').json()['job'] is None

def test_failure_retries_until_dead(tmp_path):
    c=TestClient(create_app(tmp_path/'jobs.db',max_attempts=2))
    j=c.post('/jobs',json={'task':'generate-report'}).json()['id']
    first=c.post('/worker/claim').json()['job']
    assert c.post(f'/worker/{j}/fail',json={'lease_token':first['lease_token'],'reason':'timeout'}).json()['status']=='pending'
    second=c.post('/worker/claim').json()['job']
    assert second['attempts']==2
    assert c.post(f'/worker/{j}/fail',json={'lease_token':second['lease_token'],'reason':'again'}).json()['status']=='dead'
    assert c.post('/worker/claim').json()['job'] is None

def test_expired_lease_reclaims_with_new_token(tmp_path):
    clock=[100.0]
    c=TestClient(create_app(tmp_path/'jobs.db',clock=lambda:clock[0],lease_seconds=5))
    j=c.post('/jobs',json={'task':'cleanup'}).json()['id']
    first=c.post('/worker/claim').json()['job']
    clock[0]=106
    second=c.post('/worker/claim').json()['job']
    assert second['id']==first['id']
    assert second['lease_token']!=first['lease_token']
    assert c.post(f'/worker/{j}/complete',json={'lease_token':first['lease_token']}).status_code==409
    assert c.post(f'/worker/{j}/complete',json={'lease_token':second['lease_token']}).status_code==200

def test_final_lease_timeout_goes_to_dead(tmp_path):
    clock=[10.0]
    c=TestClient(create_app(tmp_path/'jobs.db',clock=lambda:clock[0],max_attempts=1,lease_seconds=2))
    j=c.post('/jobs',json={'task':'one-shot'}).json()['id']
    c.post('/worker/claim')
    clock[0]=15
    assert c.post('/worker/claim').json()['job'] is None
    assert c.get(f'/jobs/{j}').json()['status']=='dead'

def test_missing_invalid_requests(tmp_path):
    c=TestClient(create_app(tmp_path/'jobs.db'))
    assert c.post('/jobs',json={'task':''}).status_code==422
    assert c.get('/jobs/none').status_code==404
    assert c.post('/worker/none/complete',json={'lease_token':'fake'}).status_code==404
