"""Lesson 08: distinguish authentication (401) and authorization (403)."""
import os
import secrets
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class MemoCreate(BaseModel):
    text: str = Field(min_length=1, max_length=300)


def create_app(read_key: str | None = None, admin_key: str | None = None) -> FastAPI:
    # No built-in secret: configure keys using environment variables for local use.
    reader_secret = read_key if read_key is not None else os.getenv("DEMO_READ_KEY", "")
    admin_secret = admin_key if admin_key is not None else os.getenv("DEMO_ADMIN_KEY", "")
    app = FastAPI(title="Protected Memos | API Keys")
    memos: list[str] = []

    def get_role(key: str | None = Security(key_header)) -> str:
        if not reader_secret or not admin_secret:
            raise HTTPException(status_code=503, detail="Demo API keys are not configured")
        if not key:
            raise HTTPException(status_code=401, detail="Missing API key")
        # Constant-time comparisons reduce timing information leakage.
        if secrets.compare_digest(key, admin_secret):
            return "admin"
        if secrets.compare_digest(key, reader_secret):
            return "reader"
        raise HTTPException(status_code=401, detail="Invalid API key")

    def require_admin(role: str = Depends(get_role)) -> None:
        if role != "admin":
            raise HTTPException(status_code=403, detail="Write access requires admin key")

    @app.get("/memos")
    def list_memos(_role: str = Depends(get_role)):
        return {"items": memos}

    @app.post("/memos", status_code=status.HTTP_201_CREATED)
    def add_memo(payload: MemoCreate, _admin: None = Depends(require_admin)):
        memos.append(payload.text)
        return {"id": len(memos), "text": payload.text}

    return app


app = create_app()
