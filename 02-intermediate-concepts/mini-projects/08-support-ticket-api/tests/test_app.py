from fastapi.testclient import TestClient
from app import create_app

TICKET={'customer_email':'a@example.com','subject':'Login blocked','description':'I cannot access the new account'}
role={'x-actor-role':'agent','x-actor':'student-dev'}

def test_full_workflow(tmp_path):
    with TestClient(create_app(str(tmp_path/'tickets.db'))) as c:
        r=c.post('/tickets',json=TICKET)
        assert r.status_code==201
        tid=r.json()['id']
        assert c.patch(f'/tickets/{tid}/assign',json={'assignee':'Riya'}).status_code==403
        assert c.patch(f'/tickets/{tid}/assign',json={'assignee':'Riya'},headers=role).status_code==200
        assert c.patch(f'/tickets/{tid}/status',json={'status':'resolved'},headers=role).status_code==409
        assert c.patch(f'/tickets/{tid}/status',json={'status':'in_progress'},headers=role).status_code==200
        assert c.patch(f'/tickets/{tid}/status',json={'status':'resolved'},headers=role).status_code==200
        assert c.patch(f'/tickets/{tid}/status',json={'status':'closed'},headers=role).status_code==200
        assert c.patch(f'/tickets/{tid}/assign',json={'assignee':'Riya2'},headers=role).status_code==409
        assert c.get('/tickets?status=closed').json()['items'][0]['id']==tid
        events=c.get(f'/tickets/{tid}/history',headers=role).json()['events']
        assert len(events)==5
        assert c.get(f'/tickets/{tid}/history').status_code==403

def test_missing_invalid_and_persistence(tmp_path):
    path=str(tmp_path/'a.db')
    with TestClient(create_app(path)) as c:
        assert c.get('/tickets/999').status_code==404
        assert c.post('/tickets',json={**TICKET,'customer_email':'not-email'}).status_code==422
        tid=c.post('/tickets',json=TICKET).json()['id']
    with TestClient(create_app(path)) as c:
        assert c.get(f'/tickets/{tid}').json()['subject']=='Login blocked'

def test_invalid_transition(tmp_path):
    with TestClient(create_app(str(tmp_path/'b.db'))) as c:
        tid=c.post('/tickets',json=TICKET).json()['id']
        assert c.patch(f'/tickets/{tid}/status',json={'status':'does-not-exist'},headers=role).status_code==409
