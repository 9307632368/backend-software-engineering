"""Local inventory and order workflow using SQLite BEGIN IMMEDIATE to serialize writes."""
import sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class ProductIn(BaseModel):
    sku: str = Field(min_length=2,max_length=40)
    name: str = Field(min_length=2,max_length=100)
    stock: int = Field(ge=0,le=1_000_000)
    price_paise: int = Field(ge=1,le=10_000_000)

class OrderIn(BaseModel):
    sku: str
    quantity: int = Field(gt=0,le=1000)


def create_app(db_file='orders.db'):
    app=FastAPI(title='2024 — Inventory Order Workflow')
    def db():
        c=sqlite3.connect(db_file,timeout=10,isolation_level=None)
        c.row_factory=sqlite3.Row
        c.execute('PRAGMA busy_timeout=10000')
        return c
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS products (
          sku TEXT PRIMARY KEY, name TEXT NOT NULL, stock INTEGER NOT NULL,
          reserved INTEGER NOT NULL DEFAULT 0, price_paise INTEGER NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders (
          id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL,
          quantity INTEGER NOT NULL, total_paise INTEGER NOT NULL,
          status TEXT NOT NULL, created_at TEXT NOT NULL
        )""")

    @app.post('/products',status_code=201)
    def add_product(data:ProductIn):
        with db() as c:
            try:
                c.execute('INSERT INTO products(sku,name,stock,price_paise) VALUES (?,?,?,?)',
                          (data.sku,data.name,data.stock,data.price_paise))
            except sqlite3.IntegrityError:
                raise HTTPException(409,'SKU already exists')
        return {**data.model_dump(),'reserved':0,'available':data.stock}

    @app.get('/products/{sku}')
    def product(sku:str):
        with db() as c:
            row=c.execute('SELECT * FROM products WHERE sku=?',(sku,)).fetchone()
        if not row: raise HTTPException(404,'Product not found')
        result=dict(row)
        result['available']=row['stock']-row['reserved']
        return result

    @app.post('/orders',status_code=201)
    def reserve(data:OrderIn):
        with db() as c:
            try:
                c.execute('BEGIN IMMEDIATE')
                item=c.execute('SELECT * FROM products WHERE sku=?',(data.sku,)).fetchone()
                if not item: raise HTTPException(404,'Unknown SKU')
                if item['stock']-item['reserved']<data.quantity:
                    raise HTTPException(409,'Not enough available stock')
                c.execute('UPDATE products SET reserved=reserved+? WHERE sku=?',(data.quantity,data.sku))
                cursor=c.execute("""INSERT INTO orders (sku,quantity,total_paise,status,created_at)
                         VALUES (?,?,?,'reserved',?)""",
                         (data.sku,data.quantity,data.quantity*item['price_paise'],datetime.now(timezone.utc).isoformat()))
                oid=cursor.lastrowid
                c.commit()
            except BaseException:
                c.rollback();raise
        return {'id':oid,'status':'reserved','total_paise':data.quantity*item['price_paise']}

    @app.get('/orders/{order_id}')
    def read_order(order_id:int):
        with db() as c:
            row=c.execute('SELECT * FROM orders WHERE id=?',(order_id,)).fetchone()
        if not row: raise HTTPException(404,'Order not found')
        return dict(row)

    def change_state(order_id:int,action:str):
        with db() as c:
            try:
                c.execute('BEGIN IMMEDIATE')
                order=c.execute('SELECT * FROM orders WHERE id=?',(order_id,)).fetchone()
                if not order: raise HTTPException(404,'Order not found')
                if order['status']!='reserved': raise HTTPException(409,'Order already finalized')
                if action=='confirm':
                    c.execute('UPDATE products SET stock=stock-?,reserved=reserved-? WHERE sku=?',
                              (order['quantity'],order['quantity'],order['sku']))
                    state='confirmed'
                else:
                    c.execute('UPDATE products SET reserved=reserved-? WHERE sku=?',(order['quantity'],order['sku']))
                    state='cancelled'
                c.execute('UPDATE orders SET status=? WHERE id=?',(state,order_id))
                c.commit()
                return {'id':order_id,'status':state}
            except BaseException:
                c.rollback();raise

    @app.post('/orders/{order_id}/confirm')
    def confirm(order_id:int): return change_state(order_id,'confirm')

    @app.post('/orders/{order_id}/cancel')
    def cancel(order_id:int): return change_state(order_id,'cancel')

    return app

app=create_app()
