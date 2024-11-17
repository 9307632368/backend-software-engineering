# FastAPI patterns I used

FastAPI 0.115.6 is a late-2024 release used as a reference version in the sample starter.

## Validation and responses

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

class CreateProduct(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    price_paise: int = Field(ge=0)

@app.post('/products', status_code=status.HTTP_201_CREATED)
def create_product(body: CreateProduct):
    return {'name': body.name, 'price_paise': body.price_paise}
```

I prefer integer minor units for money in small examples (`price_paise`) over floating-point rupees. For a financial system, use currency codes, decimal rules and proper ledgers.

## Dependencies

```python
from fastapi import Depends

def get_service():
    return {'environment': 'local'}

@app.get('/config')
def config(service=Depends(get_service)):
    return service
```

Replace a dependency in tests using `app.dependency_overrides`. Always clear overrides after tests, or one test can affect another.

## Async versus sync

An `async def` function helps for *nonblocking* I/O with awaitable clients. `time.sleep()` in an async endpoint blocks the event loop; use asynchronous facilities or a threadpool for blocking work. Database drivers and HTTP clients must match the chosen pattern.

## Testing

```python
from fastapi.testclient import TestClient
client = TestClient(app)
assert client.get('/openapi.json').status_code == 200
```

Run `python -m pytest -q`. Unit tests alone don't validate production database concurrency or cloud configuration.
