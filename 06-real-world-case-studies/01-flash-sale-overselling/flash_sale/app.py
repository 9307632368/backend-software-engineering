"""FastAPI demo for an inventory reservation incident."""
from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field
from .store import FlashSaleStore, StoreError


class OrderRequest(BaseModel):
    client_id: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
    sku: str = Field(min_length=2, max_length=60)
    quantity: int = Field(ge=1, le=100)


def create_app(db_path: str | Path | None = None) -> FastAPI:
    if db_path is None:
        db_path = os.getenv("FLASH_SALE_DB", str(Path(__file__).resolve().parents[1] / "data" / "flash_sale.sqlite3"))
    service = FlashSaleStore(db_path)
    api = FastAPI(title="Flash Sale Stock Reservation (study project)", version="1.0")
    api.state.store = service

    @api.get("/health")
    def health():
        return {"status": "ok"}

    @api.get("/products/{sku}")
    def product(sku: str):
        try:
            return service.get_product(sku)
        except StoreError as exc:
            raise HTTPException(exc.status_code, exc.message) from exc

    @api.post("/orders", status_code=201)
    def order(payload: OrderRequest, response: Response,
              idempotency_key: str = Header(min_length=4, max_length=100)):
        try:
            result, replayed = service.place_order(
                payload.client_id, idempotency_key, payload.sku, payload.quantity
            )
        except StoreError as exc:
            raise HTTPException(exc.status_code, exc.message) from exc
        response.status_code = 200 if replayed else 201
        response.headers["Idempotency-Replayed"] = "true" if replayed else "false"
        return result

    @api.get("/orders/{order_id}")
    def order_detail(order_id: str):
        try:
            return service.get_order(order_id)
        except StoreError as exc:
            raise HTTPException(exc.status_code, exc.message) from exc

    return api


app = create_app()
