"""Minimal HTTP adapter for the overload-control service."""
from __future__ import annotations

import os
import time
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from .service import TrafficService


def create_app(service: TrafficService | None = None, work_delay: float=0.05) -> FastAPI:
    service=service or TrafficService(
        capacity=int(os.getenv("BURST_CAPACITY","5")),
        refill_per_second=float(os.getenv("REFILL_RATE","1")),
        max_parallel=int(os.getenv("MAX_PARALLEL","2")),
    )
    api=FastAPI(title="Traffic Spike Case Study",version="1.0")
    api.state.service=service

    @api.get("/health")
    def health():
        return {"status":"ok"}  # health check bypasses rate limits

    @api.get("/work")
    def work(x_client_key: str=Header(default="anonymous",max_length=80)):
        if not x_client_key or len(x_client_key)>80:
            return JSONResponse({"error":"Invalid client key"},status_code=400)
        code,data,wait=service.process(x_client_key,lambda:(time.sleep(work_delay),{"message":"Processed"})[1])
        return JSONResponse(data,status_code=code,
                            headers={"Retry-After":str(wait)} if code in (429,503) else {})

    @api.get("/metrics")
    def metrics():
        # Exposed only as a learning shortcut; protect in deployed systems.
        return service.snapshot()

    return api


app=create_app()
