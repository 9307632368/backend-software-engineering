"""Tenant isolation with server-side API-key to tenant mapping (demo only)."""
import sqlite3
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field

class OrderIn(BaseModel):
    amount_cents: int = Field(gt=0, le=10_000_000)

DEFAULT_KEYS = {'demo-red-key':'red', 'demo-blue-key':'blue'}

def create_app(db_path='tenants.sqlite3', key_to_tenant=None):
    api = FastAPI(title='Multi Tenant Reporting Example')
    key_to_tenant = key_to_tenant or DEFAULT_KEYS
    def connect():
        db = sqlite3.connect(str(db_path),timeout=5)
        db.row_factory = sqlite3.Row
        return db
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            amount_cents INTEGER NOT NULL)""")
        db.execute('CREATE INDEX IF NOT EXISTS idx_orders_tenant ON orders(tenant_id)')

    def verified_tenant(x_api_key: str = Header(default='')):
        tenant = key_to_tenant.get(x_api_key)
        if tenant is None:
            raise HTTPException(401, 'Valid demo API key required')
        return tenant

    @api.post('/orders', status_code=201)
    def add_order(body: OrderIn, tenant: str = Depends(verified_tenant)):
        with connect() as db:
            cur = db.execute('INSERT INTO orders (tenant_id, amount_cents) VALUES (?,?)',
                             (tenant, body.amount_cents))
            return {'id':cur.lastrowid, 'tenant_id':tenant}

    @api.get('/reports/sales')
    def sales(tenant: str = Depends(verified_tenant)):
        with connect() as db:
            result = db.execute("""SELECT COUNT(*) AS orders,
                COALESCE(SUM(amount_cents),0) AS total_cents FROM orders WHERE tenant_id=?""",
                (tenant,)).fetchone()
        return {'tenant_id':tenant, **dict(result)}

    @api.get('/orders')
    def list_orders(tenant: str = Depends(verified_tenant)):
        with connect() as db:
            return [dict(r) for r in db.execute('SELECT id,amount_cents FROM orders WHERE tenant_id=? ORDER BY id', (tenant,))]

    return api

app = create_app()
