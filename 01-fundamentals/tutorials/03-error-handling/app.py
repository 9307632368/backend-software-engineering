"""Lesson 03: meaningful API errors instead of silent failures."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Stock Reservation | API Errors")

# Deliberately immutable demo inventory; requests only show what would be reserved.
STOCK = {"mouse": 12, "keyboard": 4, "monitor": 0}


class ReservationRequest(BaseModel):
    sku: str = Field(min_length=2)
    quantity: int = Field(gt=0, le=20)


@app.get("/stock/{sku}")
def stock_level(sku: str):
    if sku not in STOCK:
        raise HTTPException(status_code=404, detail="Product does not exist")
    return {"sku": sku, "available": STOCK[sku]}


@app.post("/reservations/check")
def check_reservation(payload: ReservationRequest):
    if payload.sku not in STOCK:
        raise HTTPException(status_code=404, detail="Product does not exist")
    if STOCK[payload.sku] == 0:
        raise HTTPException(status_code=409, detail="Item is out of stock")
    if payload.quantity > STOCK[payload.sku]:
        raise HTTPException(
            status_code=409,
            detail={"message": "Not enough stock", "available": STOCK[payload.sku]},
        )
    return {"sku": payload.sku, "quantity": payload.quantity, "can_reserve": True}
