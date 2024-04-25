"""Checkout request simulation with durable idempotency keys; does not charge cards."""
import hashlib
import json
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

class CheckoutIn(BaseModel):
    customer_id: str = Field(min_length=2,max_length=50)
    item_sku: str = Field(min_length=2,max_length=50)
    quantity: int = Field(ge=1,le=20)
    unit_price_paise: int = Field(gt=0,le=1_000_000)

def create_app(db_file='checkout.db'):
    app=FastAPI(title='2024 — Idempotent Checkout Demo')
    def open_db():
        conn=sqlite3.connect(db_file,timeout=10,isolation_level=None)
        conn.row_factory=sqlite3.Row
        conn.execute('PRAGMA busy_timeout=10000')
        return conn
    with open_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS checkout (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idempotency_key TEXT NOT NULL UNIQUE,
            fingerprint TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            item_sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_paise INTEGER NOT NULL,
            state TEXT NOT NULL
        )""")

    @app.post('/checkouts', status_code=201)
    def checkout(payload: CheckoutIn, idempotency_key: str | None = Header(default=None)):
        if not idempotency_key or len(idempotency_key)>120:
            raise HTTPException(400,'Idempotency-Key header must be 1-120 characters')
        normalized=payload.model_dump_json()
        fingerprint=hashlib.sha256(normalized.encode()).hexdigest()
        with open_db() as conn:
            try:
                conn.execute('BEGIN IMMEDIATE')
                row=conn.execute('SELECT * FROM checkout WHERE idempotency_key=?',(idempotency_key,)).fetchone()
                if row:
                    if row['fingerprint']!=fingerprint:
                        raise HTTPException(409,'Key already used for a different request')
                    conn.commit()
                    return {k:v for k,v in dict(row).items() if k not in {'fingerprint','idempotency_key'}} | {'replayed':True}
                total=payload.quantity*payload.unit_price_paise
                cursor=conn.execute("""INSERT INTO checkout
                    (idempotency_key,fingerprint,customer_id,item_sku,quantity,total_paise,state)
                    VALUES (?,?,?,?,?,?,?)""",
                    (idempotency_key,fingerprint,payload.customer_id,payload.item_sku,payload.quantity,total,'accepted'))
                row=conn.execute('SELECT * FROM checkout WHERE id=?',(cursor.lastrowid,)).fetchone()
                conn.commit()
                return {k:v for k,v in dict(row).items() if k not in {'fingerprint','idempotency_key'}} | {'replayed':False}
            except BaseException:
                conn.rollback()
                raise

    @app.get('/checkouts/{checkout_id}')
    def get_checkout(checkout_id: int):
        with open_db() as conn:
            row=conn.execute('SELECT * FROM checkout WHERE id=?',(checkout_id,)).fetchone()
        if row is None: raise HTTPException(404,'Checkout not found')
        result=dict(row)
        result.pop('fingerprint')
        result.pop('idempotency_key')
        return result

    return app

app=create_app()
