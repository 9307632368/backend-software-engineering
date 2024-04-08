"""Structured request logging with settings read from environment variables."""
import json
import logging
import os
from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

@dataclass(frozen=True)
class Settings:
    app_env: str = "development"
    max_items: int = 100

    @classmethod
    def from_env(cls):
        max_items = int(os.getenv("MAX_ITEMS", "100"))
        if max_items < 1:
            raise ValueError("MAX_ITEMS must be positive")
        return cls(app_env=os.getenv("APP_ENV", "development"), max_items=max_items)

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=80)

def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else Settings.from_env()
    api = FastAPI(title="Logging and Configuration Example")
    logger = logging.getLogger("backend.examples.request")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    items: list[str] = []

    @api.middleware("http")
    async def request_logger(request: Request, call_next):
        request_id = uuid4().hex
        started = perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Do not log query strings, authorization headers, or bodies.
            event = {"event": "http_request", "method": request.method, "path": request.url.path,
                     "status": status, "duration_ms": round((perf_counter() - started) * 1000, 2),
                     "request_id": request_id}
            logger.info(json.dumps(event))

    @api.get("/health")
    def health():
        return {"status": "ok", "environment": config.app_env}

    @api.post("/items", status_code=201)
    def add_item(item: Item):
        if len(items) >= config.max_items:
            raise HTTPException(409, "Item capacity reached")
        items.append(item.name)
        return {"id": len(items), "name": item.name}

    @api.get("/items")
    def list_items(limit: int = Query(10, ge=1, le=100)):
        return {"items": items[:limit], "count": len(items)}

    return api

app = create_app()
