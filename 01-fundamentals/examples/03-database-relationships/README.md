# 03 — Database relationships

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Create users and products, then place orders that refer to them.

2024-level concepts: SQLite, SQLAlchemy 2, foreign keys, relationships, transactions, integer money amounts.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Create a user and product, place an order, list the user’s orders. Then try ordering more stock than is available.

### Simple data relationship
`User 1 -> many Orders -> many OrderLines -> one Product`. The order keeps a copy of the price at checkout, so changing a product price later does not silently change old orders. Money is expressed as integer cents to avoid floating-point rounding.

## How it can be improved

The stock check is not enough for concurrent purchases. Production needs database-specific locking, migrations, transaction isolation strategy and authentication.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_03_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
