"""Simulated independent I/O calls to understand async.gather and timeout."""
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title='2024 — Async I/O Practice')

class CheckRequest(BaseModel):
    sku: str = Field(min_length=2, max_length=30)
    timeout_ms: int = Field(default=500, ge=1, le=10_000)

async def get_stock(sku: str):
    await asyncio.sleep(0.01)  # simulates network waiting; does not block event loop
    return {'sku':sku, 'stock':12}

async def get_shipping(sku: str):
    await asyncio.sleep(0.01)
    return {'sku':sku, 'delivery_days':3}

@app.post('/availability')
async def availability(payload: CheckRequest):
    try:
        stock, shipping = await asyncio.wait_for(
            asyncio.gather(get_stock(payload.sku), get_shipping(payload.sku)),
            timeout=payload.timeout_ms / 1000,
        )
    except asyncio.TimeoutError:
        raise HTTPException(504, detail='Upstream services took too long')
    return {'sku':payload.sku, 'stock':stock['stock'], 'delivery_days':shipping['delivery_days']}
