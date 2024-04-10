"""Lesson 07: predictable sorting, search and offset pagination."""
from typing import Literal
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Product Catalog | Pagination and Filtering")

CATALOG = [
    {"id": 1, "name": "USB-C Cable", "category": "accessories", "price_paise": 49900},
    {"id": 2, "name": "Wireless Mouse", "category": "accessories", "price_paise": 89900},
    {"id": 3, "name": "Laptop Stand", "category": "office", "price_paise": 159900},
    {"id": 4, "name": "Desk Lamp", "category": "office", "price_paise": 119900},
    {"id": 5, "name": "Keyboard", "category": "accessories", "price_paise": 129900},
    {"id": 6, "name": "Notebook", "category": "office", "price_paise": 9900},
]


class CatalogPage(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool
    items: list[dict]


@app.get("/catalog", response_model=CatalogPage)
def list_catalog(
    category: str | None = None,
    search: str | None = Query(default=None, min_length=2),
    sort_by: Literal["id", "name", "price_paise"] = "id",
    order: Literal["asc", "desc"] = "asc",
    limit: int = Query(default=3, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items = CATALOG
    if category:
        items = [item for item in items if item["category"] == category]
    if search:
        items = [item for item in items if search.casefold() in item["name"].casefold()]
    items = sorted(items, key=lambda item: item[sort_by], reverse=(order == "desc"))
    total = len(items)
    page = items[offset:offset + limit]
    return {"total": total, "offset": offset, "limit": limit,
            "has_more": offset + len(page) < total, "items": page}
