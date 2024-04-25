"""Small demonstration of reusable FastAPI dependencies and environment settings."""
import os
from dataclasses import dataclass
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

@dataclass(frozen=True)
class Settings:
    application_name: str
    api_key: str
    tax_percent: int

def get_settings() -> Settings:
    # Read settings on each request so local tests can replace dependencies easily.
    return Settings(
        application_name=os.getenv('APP_NAME', 'Invoice Practice API'),
        api_key=os.getenv('DEMO_API_KEY', ''),
        tax_percent=int(os.getenv('TAX_PERCENT', '5')),
    )

def check_key(x_api_key: str | None = Header(default=None), cfg: Settings = Depends(get_settings)):
    if not cfg.api_key or x_api_key != cfg.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Valid API key required')
    return 'demo-client'

class QuoteRequest(BaseModel):
    description: str = Field(min_length=2, max_length=80)
    unit_price_paise: int = Field(ge=0)
    units: int = Field(ge=1, le=1000)

class QuoteResponse(BaseModel):
    description: str
    subtotal_paise: int
    tax_paise: int
    total_paise: int

app = FastAPI(title='2024 — Dependencies and Settings')

@app.get('/health')
def health(settings: Settings = Depends(get_settings)):
    return {'status': 'ok', 'service': settings.application_name}

@app.post('/quotes', response_model=QuoteResponse, dependencies=[Depends(check_key)])
def create_quote(data: QuoteRequest, settings: Settings = Depends(get_settings)):
    subtotal = data.unit_price_paise * data.units
    tax = (subtotal * settings.tax_percent + 50) // 100
    return QuoteResponse(description=data.description, subtotal_paise=subtotal,
                         tax_paise=tax, total_paise=subtotal + tax)
