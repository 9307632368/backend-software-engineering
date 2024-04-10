# 2024 Package Versions

The purpose of the versions here is to reproduce a **2024-level learning environment**, not to claim these files were authored in 2024. The primary local target is **Python 3.11**.

| Package | Pinned version | Release during 2024 |
|---|---|---|
| FastAPI | 0.115.6 | 3 Dec 2024 |
| Pydantic | 2.10.4 | 18 Dec 2024 |
| Uvicorn | 0.32.1 | 20 Nov 2024 |
| SQLAlchemy | 2.0.36 | 15 Oct 2024 |
| PyJWT | 2.10.1 | 28 Nov 2024 |
| python-multipart | 0.0.20 | 16 Dec 2024 |
| redis-py | 5.2.1 | 6 Dec 2024 |
| HTTPX (tests) | 0.27.2 | 27 Aug 2024 |
| pytest (tests) | 8.3.4 | Dec 2024 |
| fakeredis (optional tests) | 2.26.2 | 17 Dec 2024 |

The Docker file uses the Redis **7.4.2** image tag, from the 2024 Redis 7.4 series, in a local-only demo.

**Why exact versions?** A tutorial can stop working if a framework changes endpoint/test behavior. A pinned learning environment is easier to reproduce. For production, use supported and patched versions with an upgraded dependency lock and review breaking changes.

**Verification limitation:** The development machine used to build this archive could not download historical pins. The included API tests were run against the available installed packages. The pinned environment is designed for reproduction but has not been independently installed and tested in this environment.

## Release documentation

- [FastAPI 0.115.6](https://pypi.org/project/fastapi/0.115.6/)
- [Pydantic release history](https://pypi.org/project/pydantic/#history)
- [Uvicorn release history](https://www.uvicorn.org/release-notes/)
- [SQLAlchemy 2.0.36](https://pypi.org/project/SQLAlchemy/2.0.36/)
- [PyJWT 2.10.1](https://pypi.org/project/PyJWT/2.10.1/)
- [python-multipart 0.0.20](https://pypi.org/project/python-multipart/0.0.20/)
- [redis 5.2.1](https://pypi.org/project/redis/5.2.1/)
- [HTTPX 0.27.2](https://pypi.org/project/httpx/0.27.2/)
- [pytest 8.3.4](https://pypi.org/project/pytest/8.3.4/)
- [fakeredis history](https://pypi.org/project/fakeredis/#history)
