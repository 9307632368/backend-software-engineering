"""Versioned API contracts with nested validation and filtered response model."""
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict, field_validator

class Priority(str,Enum):
    normal='normal'
    urgent='urgent'

class Address(BaseModel):
    city: str = Field(min_length=2, max_length=60)
    postal_code: str = Field(pattern=r'^[0-9]{6}$')

class ShipmentIn(BaseModel):
    model_config=ConfigDict(extra='forbid')
    customer_name: str = Field(min_length=2, max_length=80)
    address: Address
    boxes: int = Field(ge=1,le=25)
    priority: Priority = Priority.normal
    internal_note: str | None = None

    @field_validator('customer_name')
    @classmethod
    def normalize_name(cls,value):
        return ' '.join(value.split())

class ShipmentOut(BaseModel):
    tracking_ref: str
    customer_name: str
    priority: Priority
    estimated_days: int

app = FastAPI(title='2024 — API Contracts')

@app.post('/v1/shipments',response_model=ShipmentOut,status_code=201)
def create_shipment(shipment:ShipmentIn):
    return {'tracking_ref':'DEMO-0001', 'customer_name':shipment.customer_name,
            'priority':shipment.priority, 'estimated_days':1 if shipment.priority==Priority.urgent else 4,
            'internal_note':shipment.internal_note}  # filtered out by response_model
