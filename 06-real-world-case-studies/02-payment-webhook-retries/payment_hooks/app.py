"""Signed webhook receiving and replay-safe local payment records."""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from .store import PaymentStore, StoreError


class PaymentIn(BaseModel):
    payment_id: str=Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    amount_cents: int=Field(gt=0, le=100_000_000)


class WebhookIn(BaseModel):
    event_id: str=Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    payment_id: str=Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    type: Literal["payment.succeeded", "payment.failed"]
    amount_cents: int=Field(gt=0, le=100_000_000)


def sign(secret: str, timestamp: int, body: bytes) -> str:
    message=str(timestamp).encode()+b"."+body
    return hmac.new(secret.encode(),message,hashlib.sha256).hexdigest()


def create_app(db_path: str | Path | None = None, secret: str | None = None,
               internal_key: str | None = None, clock=None) -> FastAPI:
    if db_path is None:
        db_path=os.getenv("PAYMENT_DB",str(Path(__file__).resolve().parents[1]/"data"/"payment.sqlite3"))
    secret=secret if secret is not None else os.getenv("WEBHOOK_SECRET","local-demo-only-webhook-secret")
    internal_key=internal_key if internal_key is not None else os.getenv("INTERNAL_API_KEY","local-demo-only-internal-key")
    clock=clock or time.time
    db=PaymentStore(db_path)
    api=FastAPI(title="Payment Webhook Retry Case Study",version="1.0")
    api.state.store=db

    def check_key(header: str | None):
        if not header or not hmac.compare_digest(header,internal_key):
            raise HTTPException(401,"Invalid internal API key")

    @api.get("/health")
    def health():
        return {"status":"ok"}

    @api.post("/internal/payments",status_code=201)
    def register(payload: PaymentIn, x_internal_api_key: str | None = Header(default=None)):
        check_key(x_internal_api_key)
        try: return db.create_payment(payload.payment_id,payload.amount_cents)
        except StoreError as e: raise HTTPException(e.code,e.message) from e

    @api.get("/internal/payments/{payment_id}")
    def lookup(payment_id: str, x_internal_api_key: str | None = Header(default=None)):
        check_key(x_internal_api_key)
        try:return db.get_payment(payment_id)
        except StoreError as e:raise HTTPException(e.code,e.message) from e

    @api.post("/webhooks/payment")
    async def receive(request:Request,
                      x_webhook_timestamp: str | None=Header(default=None),
                      x_webhook_signature: str | None=Header(default=None)):
        # Verify the signature over RAW bytes before parsing JSON.
        body=await request.body()
        try:
            timestamp=int(x_webhook_timestamp or "")
        except ValueError:
            raise HTTPException(401,"Invalid or missing timestamp")
        if abs(clock()-timestamp)>300:
            raise HTTPException(401,"Timestamp outside the five-minute window")
        expected=sign(secret,timestamp,body)
        if not x_webhook_signature or not hmac.compare_digest(expected,x_webhook_signature):
            raise HTTPException(401,"Invalid webhook signature")
        try:
            payload=WebhookIn.model_validate_json(body)
        except ValidationError as e:
            raise HTTPException(422,"Invalid webhook payload") from e
        try:
            outcome,duplicate=db.ingest_event(payload.model_dump())
        except StoreError as e:
            raise HTTPException(e.code,e.message) from e
        return JSONResponse({"outcome":outcome,"duplicate":duplicate},
                            status_code=202 if outcome=="awaiting_payment" else 200)

    @api.post("/internal/reconcile")
    def reconcile(x_internal_api_key: str | None=Header(default=None)):
        check_key(x_internal_api_key)
        return db.reconcile()

    @api.get("/internal/event-stats")
    def stats(x_internal_api_key: str | None=Header(default=None)):
        check_key(x_internal_api_key)
        return db.stats()

    return api


app=create_app()
