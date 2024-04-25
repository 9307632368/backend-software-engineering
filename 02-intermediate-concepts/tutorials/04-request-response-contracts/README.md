# Tutorial 04 — Request and Response Contracts

I practiced nested Pydantic models, enums, reusable constraints, validators, API version prefixes, and response filtering. This sample deliberately accepts an internal note but **does not return it**.

Run `python -m uvicorn app:app --reload` and open `/docs`. Submit invalid postal codes or unexpected request fields to see helpful 422 errors.

**Practice:** add a `phone_number` validator, design a separate `ShipmentUpdate` model, and explain when API versioning is useful.
