# Local validation

The three cases were run in the available test environment.

```text
$ python -m pytest -q
28 passed
```

**Limitation:** The test environment used its preinstalled newer packages (Python 3.13, FastAPI 0.128.2, Pydantic 2.13.5, pytest 9.0.2). The supplied `requirements-2024.txt` selects releases available by December 2024, but that exact historical environment has not been separately installed or verified here.

All scenarios are synthetic and no production loads or payment providers were used.
