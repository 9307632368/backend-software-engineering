"""Interview practice 01: idempotent payment-like requests with SQLite.

This is a payment *simulation*, not a payment gateway or PCI implementation.
"""
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


class PaymentIn(BaseModel):
    customer_id: str = Field(min_length=1, max_length=80)
    amount_paise: int = Field(gt=0, le=50_000_000)
    currency: str = Field(default='INR', pattern=r'^INR$')


def create_app(db_path: str = 'payments.sqlite3') -> FastAPI:
    app = FastAPI(title='Interview 01 - Idempotent Payment Simulation')
    path = str(Path(db_path))
    with closing(sqlite3.connect(path)) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            idempotency_key TEXT NOT NULL,
            amount_paise INTEGER NOT NULL,
            currency TEXT NOT NULL,
            UNIQUE(customer_id, idempotency_key)
        )''')
        conn.commit()

    @app.post('/payments', status_code=201)
    def create_payment(payload: PaymentIn, idempotency_key: Annotated[str, Header(min_length=1, max_length=128, alias='Idempotency-Key')]):
        with closing(sqlite3.connect(path, timeout=10, isolation_level=None)) as conn:
            conn.row_factory = sqlite3.Row
            try:
                # Serialize writers. A duplicate request cannot create a second row.
                conn.execute('BEGIN IMMEDIATE')
                existing = conn.execute(
                    'SELECT * FROM payments WHERE customer_id=? AND idempotency_key=?',
                    (payload.customer_id, idempotency_key)
                ).fetchone()
                if existing:
                    if (existing['amount_paise'], existing['currency']) != (payload.amount_paise, payload.currency):
                        conn.execute('ROLLBACK')
                        raise HTTPException(409, 'Key already used with different payment details')
                    result = dict(existing)
                    conn.execute('COMMIT')
                    return {'payment_id': result['id'], 'amount_paise': result['amount_paise'],
                            'currency': result['currency'], 'replayed': True}
                cursor = conn.execute(
                    'INSERT INTO payments(customer_id,idempotency_key,amount_paise,currency) VALUES(?,?,?,?)',
                    (payload.customer_id, idempotency_key, payload.amount_paise, payload.currency)
                )
                conn.execute('COMMIT')
                return {'payment_id': cursor.lastrowid, 'amount_paise': payload.amount_paise,
                        'currency': payload.currency, 'replayed': False}
            except Exception:
                if conn.in_transaction:
                    conn.execute('ROLLBACK')
                raise

    @app.get('/payments/count')
    def payment_count():
        with closing(sqlite3.connect(path)) as conn:
            return {'count': conn.execute('SELECT COUNT(*) FROM payments').fetchone()[0]}

    return app


app = create_app()
