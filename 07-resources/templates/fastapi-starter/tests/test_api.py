import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_data


@pytest.fixture(autouse=True)
def fresh_state():
    reset_data()
    yield
    reset_data()


client = TestClient(app)


def test_health():
    assert client.get('/health').json() == {'status': 'ok'}


def test_create_and_read():
    created = client.post('/tasks', json={'title': 'Finish API lesson', 'priority': 1})
    assert created.status_code == 201
    assert created.json()['id'] == 1
    assert client.get('/tasks/1').json()['title'] == 'Finish API lesson'


def test_invalid_title():
    assert client.post('/tasks', json={'title': 'a'}).status_code == 422


def test_invalid_priority():
    assert client.post('/tasks', json={'title': 'Read docs', 'priority': 8}).status_code == 422


def test_not_found():
    assert client.get('/tasks/99').status_code == 404


def test_complete_and_filter():
    client.post('/tasks', json={'title': 'Write tests'})
    client.post('/tasks', json={'title': 'Read examples'})
    assert client.patch('/tasks/1').json()['done'] is True
    assert len(client.get('/tasks?done=true').json()) == 1
    assert len(client.get('/tasks?done=false').json()) == 1


def test_delete_returns_204():
    client.post('/tasks', json={'title': 'Temporary task'})
    response = client.delete('/tasks/1')
    assert response.status_code == 204
    assert response.content == b''
    assert client.get('/tasks/1').status_code == 404


def test_tasks_sorted_by_id():
    for name in ['First job', 'Second job', 'Third job']:
        client.post('/tasks', json={'title': name})
    assert [row['id'] for row in client.get('/tasks').json()] == [1, 2, 3]
