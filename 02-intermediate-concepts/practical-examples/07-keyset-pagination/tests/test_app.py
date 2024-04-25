from fastapi.testclient import TestClient
from app import create_app

def test_cursor_pages_and_filters(tmp_path):
    with TestClient(create_app(str(tmp_path/'a.db'))) as c:
        for i in range(6):
            assert c.post('/products',json={'name':f'Item {i}','category':'tools' if i%2==0 else 'books','price_paise':100+i*100}).status_code==201
        first=c.get('/products?limit=2').json()
        second=c.get('/products',params={'limit':2,'after':first['next_cursor']}).json()
        assert [item['id'] for item in first['items']]==[1,2]
        assert [item['id'] for item in second['items']]==[3,4]
        filtered=c.get('/products',params={'category':'tools','min_price_paise':400}).json()
        assert [row['id'] for row in filtered['items']]==[5]

def test_bad_limit(tmp_path):
    with TestClient(create_app(str(tmp_path/'b.db'))) as c:
        assert c.get('/products?limit=0').status_code==422
        assert c.get('/products?after=-3').status_code==422

def test_end_cursor(tmp_path):
    with TestClient(create_app(str(tmp_path/'c.db'))) as c:
        c.post('/products',json={'name':'Pencil','category':'office','price_paise':50})
        page=c.get('/products?limit=4').json()
        assert page['next_cursor'] is None
        assert not page['has_more']
