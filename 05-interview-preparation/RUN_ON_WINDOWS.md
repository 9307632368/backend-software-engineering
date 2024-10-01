# How to run on Windows (PowerShell)

Open PowerShell **inside** your `05-interview-preparation` directory.

## Install once

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If PowerShell blocks the activation script, you can skip activation and use `.\.venv\Scripts\python.exe` instead of `python` in the commands.

## Check all coding rounds

```powershell
python -m pytest -q
```

## Run one API

```powershell
python -m uvicorn hands_on.concurrent_stock_orders:app --reload
```

In your browser, visit <http://127.0.0.1:8000/docs>. Use the interactive **Try it out** button for POST and GET requests. To stop the server, press **Ctrl+C**.

Other choices:

```powershell
python -m uvicorn hands_on.sliding_window_rate_limit:app --reload
python -m uvicorn hands_on.audit_log_pagination:app --reload
python -m uvicorn hands_on.signed_webhook:app --reload
python -m uvicorn hands_on.retry_job_queue:app --reload
```

**Data:** the default payment, stock, audit and job examples create local `.sqlite3` files. Those are intentionally excluded from Git. Tests create isolated temporary databases.

**Security:** do not publish personal credentials, webhook secrets or real customer information. The demonstration secret in the webhook file is for practice only.
