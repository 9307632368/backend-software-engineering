# PowerShell instructions

Use Python 3.11 to approximate a typical late-2024 environment. Open PowerShell **inside `06-real-world-case-studies`**.

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-2024.txt
python -m pytest -q
```

Then open separate terminals for individual cases, for example:

```powershell
cd 03-api-traffic-spike
python -m uvicorn traffic_spike.app:app --reload
```

To deactivate the environment, run `deactivate`. To use a different port, add `--port 8001`.

If activating the environment is blocked by your PowerShell policy, you can call `.\.venv\Scripts\python.exe -m pytest -q` directly from the root.
