"""Interview practice 03: atomic inventory deductions under concurrent orders."""
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class StockIn(BaseModel):
    sku: str = Field(min_length=3, max_length=32)
    quantity: int = Field(ge=0, le=1_000_000)


class OrderIn(BaseModel):
    sku: str = Field(min_length=3, max_length=32)
    quantity: int = Field(gt=0, le=1_000_000)


def create_app(db_path: str = 'stock.sqlite3') -> FastAPI:
    app = FastAPI(title='Interview 03 - Atomic Stock Orders')
    db_path = str(Path(db_path))
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, available INTEGER NOT NULL CHECK(available >= 0));
        CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL,
                                           quantity INTEGER NOT NULL CHECK(quantity > 0));
        ''')

    @app.post('/stock', status_code=201)
    def create_stock(item: StockIn):
        with closing(sqlite3.connect(db_path)) as conn:
            try:
                conn.execute('INSERT INTO stock(sku,available) VALUES(?,?)', (item.sku, item.quantity))
                conn.commit()
            except sqlite3.IntegrityError:
                raise HTTPException(409, 'SKU already exists')
        return item.model_dump()

    @app.post('/orders', status_code=201)
    def place_order(order: OrderIn):
        with closing(sqlite3.connect(db_path, timeout=10, isolation_level=None)) as conn:
            try:
                conn.execute('BEGIN IMMEDIATE')
                # Never read stock in Python and then overwrite it: that can oversell.
                result = conn.execute('UPDATE stock SET available=available-? WHERE sku=? AND available>=?',
                                      (order.quantity, order.sku, order.quantity))
                if result.rowcount != 1:
                    exists = conn.execute('SELECT 1 FROM stock WHERE sku=?', (order.sku,)).fetchone()
                    conn.execute('ROLLBACK')
                    raise HTTPException(409 if exists else 404,
                                        'Not enough stock' if exists else 'Unknown SKU')
                order_id = conn.execute('INSERT INTO orders(sku,quantity) VALUES(?,?)',
                                        (order.sku, order.quantity)).lastrowid
                conn.execute('COMMIT')
                return {'order_id': order_id, **order.model_dump()}
            except Exception:
                if conn.in_transaction:
                    conn.execute('ROLLBACK')
                raise

    @app.get('/stock/{sku}')
    def get_stock(sku: str):
        with closing(sqlite3.connect(db_path)) as conn:
            row = conn.execute('SELECT available FROM stock WHERE sku=?', (sku,)).fetchone()
        if not row:
            raise HTTPException(404, 'Unknown SKU')
        return {'sku': sku, 'available': row[0]}

    return app


app = create_app()
