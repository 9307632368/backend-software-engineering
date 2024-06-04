# 04. URL shortener — system design + API

A URL shortener looks easy until you start thinking about **unique IDs, expiry, read traffic and redirects**. This folder includes an API you can run and a system-design note with assumptions and a scaling plan.

Quick experiment: create a link with `POST /links`, visit `/r/{code}`, and inspect `/links/{code}/stats`. The redirect is 307 and counts a hit before responding. Tests cover expiry and token collisions.

Run `python -m uvicorn app:app --reload` or `python -m pytest -q tests`.

**Not for public internet hosting without changes.** This example has no abuse detection or user authentication, supports arbitrary web destinations, and stores hit counts on each redirect (a database write bottleneck). See `DESIGN.md`.
