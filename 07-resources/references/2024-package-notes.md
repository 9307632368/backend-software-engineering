# Versions used in the included FastAPI starter

I used releases that existed by **31 Dec 2024**, rather than automatically installing the latest version.

| Package | Version |
|---|---|
| Python runtime | 3.11 |
| FastAPI | 0.115.6 |
| Uvicorn | 0.32.1 |
| Pydantic | 2.10.4 |
| httpx | 0.28.1 |
| pytest | 8.3.4 |

These are learning pins for reproducing a historical stack. They do not mean the packages have current security support. The exact pinned set might need compatibility and security review on your system.

The resource tools (`tools/`) use only the Python standard library and can be tested without installing the FastAPI dependencies.
