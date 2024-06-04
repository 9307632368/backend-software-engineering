"""Atomic order/outbox storage; manual dispatcher models at-least-once events."""
import json
import sqlite3
import uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field

class NewOrder(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    quantity: int = Field(ge=1, le=100)

class InMemoryPublisher:
    def __init__(self):
        self.fail_next = False
        self.published = []

    def publish(self, event_id, payload):
        if self.fail_next:
            self.fail_next = False
            raise OSError('Simulated broker outage')
        self.published.append((event_id, payload))

def create_app(db_path='outbox.sqlite3', publisher=None):
    api = FastAPI(title='Transactional Outbox Demo')
    publisher = publisher or InMemoryPublisher()
    api.state.publisher = publisher

    def connect():
        db = sqlite3.connect(str(db_path), timeout=5)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, sku TEXT NOT NULL, quantity INTEGER NOT NULL)')
        db.execute("""CREATE TABLE IF NOT EXISTS outbox
            (id TEXT PRIMARY KEY, order_id TEXT NOT NULL, payload TEXT NOT NULL,
             status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0)""")

    @api.post('/orders', status_code=201)
    def create_order(body: NewOrder):
        order_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        with connect() as db:
            db.execute('INSERT INTO orders (id, sku, quantity) VALUES (?, ?, ?)', (order_id, body.sku, body.quantity))
            payload = {'type': 'OrderCreated', 'order_id':order_id, 'sku':body.sku, 'quantity':body.quantity}
            db.execute('INSERT INTO outbox (id, order_id, payload) VALUES (?, ?, ?)', (event_id, order_id, json.dumps(payload)))
        return {'id':order_id, 'event_id':event_id}

    @api.get('/events')
    def list_events():
        with connect() as db:
            return [dict(r) for r in db.execute('SELECT id, order_id, status, attempts FROM outbox ORDER BY rowid')]

    @api.post('/worker/dispatch')
    def dispatch():
        sent = failed = 0
        with connect() as db:
            items = db.execute("SELECT * FROM outbox WHERE status='pending' ORDER BY rowid LIMIT 20").fetchall()
        for item in items:
            try:
                publisher.publish(item['id'], json.loads(item['payload']))
            except OSError:
                failed += 1
                with connect() as db:
                    db.execute('UPDATE outbox SET attempts = attempts + 1 WHERE id = ?', (item['id'],))
            else:
                sent += 1
                with connect() as db:
                    db.execute("UPDATE outbox SET status='sent', attempts = attempts + 1 WHERE id = ?", (item['id'],))
        return {'sent': sent, 'failed': failed}

    return api

app = create_app()
