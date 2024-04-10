"""Lesson 06: separate pricing rules from HTTP routes and override services in tests."""
from typing import Annotated
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Shipping Quotes | Dependencies")


class ShippingQuote(BaseModel):
    distance_km: int
    weight_grams: int
    priority: bool
    total_paise: int
    currency: str = "INR"


class PricingService:
    def calculate_paise(self, distance_km: int, weight_grams: int, priority: bool) -> int:
        # Money is stored in paise to avoid floating point rounding for prices.
        base_paise = 5000
        distance_paise = distance_km * 150
        weight_paise = ((weight_grams + 999) // 1000) * 1200
        priority_paise = 2500 if priority else 0
        return base_paise + distance_paise + weight_paise + priority_paise


def get_pricing_service() -> PricingService:
    return PricingService()


@app.get("/shipping/quote", response_model=ShippingQuote)
def quote_shipping(
    distance_km: Annotated[int, Query(ge=1, le=5000)],
    weight_grams: Annotated[int, Query(ge=1, le=50000)],
    priority: bool = False,
    service: PricingService = Depends(get_pricing_service),
):
    return ShippingQuote(
        distance_km=distance_km,
        weight_grams=weight_grams,
        priority=priority,
        total_paise=service.calculate_paise(distance_km, weight_grams, priority),
    )
