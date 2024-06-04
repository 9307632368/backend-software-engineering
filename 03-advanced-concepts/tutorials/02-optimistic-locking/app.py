"""Versioned stock updates. Separate connections permit realistic concurrency tests."""
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class StockChange(BaseModel):
    expected_version: int = Field(ge=1)
    delta: int = Field(ge=-10000, le=10000)

def create_app(db_path='stock.sqlite3'):
    api = FastAPI(title='Optimistic Locking Demo')
    db_path = str(db_path)

    def connect():
        connection = sqlite3.connect(db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, stock INTEGER NOT NULL, version INTEGER NOT NULL)')
        db.execute("INSERT OR IGNORE INTO products VALUES (1, 'USB Cable', 10, 1)")

    @api.get('/products/{product_id}')
    def get_product(product_id: int):
        with connect() as db:
            row = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Product not found')
        return dict(row)

    @api.patch('/products/{product_id}/stock')
    def update_stock(product_id: int, change: StockChange):
        with connect() as db:
            # The version predicate is what prevents a stale writer from winning.
            cursor = db.execute("""UPDATE products
                SET stock = stock + ?, version = version + 1
                WHERE id = ? AND version = ? AND stock + ? >= 0""",
                (change.delta, product_id, change.expected_version, change.delta))
            if cursor.rowcount == 1:
                row = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
                return dict(row)
            row = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
            if row is None:
                raise HTTPException(404, 'Product not found')
            if row['version'] != change.expected_version:
                raise HTTPException(409, 'Stale version; fetch latest product and retry')
            raise HTTPException(422, 'Insufficient stock')

    return api

app = create_app()
