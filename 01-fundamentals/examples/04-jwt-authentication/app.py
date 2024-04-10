"""Small JWT authorization demo. Signing key must be set in the environment."""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

bearer = HTTPBearer(auto_error=False)

class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=8, max_length=100)

def password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password: str, value: str) -> bool:
    salt, digest = value.split(":", 1)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000)
    return hmac.compare_digest(candidate, bytes.fromhex(digest))

def create_app(secret_key: str = "", token_minutes: int = 20) -> FastAPI:
    api = FastAPI(title="JWT Authentication Example")
    users: dict[str, str] = {}

    @api.post("/register", status_code=201)
    def register(payload: Credentials):
        if payload.username in users:
            raise HTTPException(409, "Username exists")
        users[payload.username] = password_hash(payload.password)
        return {"username": payload.username}

    @api.post("/token")
    def token(payload: Credentials):
        stored = users.get(payload.username)
        if not stored or not verify_password(payload.password, stored):
            raise HTTPException(401, "Invalid credentials")
        if len(secret_key) < 32:
            raise HTTPException(503, "Configure JWT_SECRET_KEY (32+ characters) before using tokens")
        expiry = datetime.now(timezone.utc) + timedelta(minutes=token_minutes)
        value = jwt.encode({"sub": payload.username, "exp": expiry}, secret_key, algorithm="HS256")
        return {"access_token": value, "token_type": "bearer"}

    def current_user(auth: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
        if not auth or len(secret_key) < 32:
            raise HTTPException(401, "Bearer token required")
        try:
            claims = jwt.decode(auth.credentials, secret_key, algorithms=["HS256"], options={"require": ["sub", "exp"]})
            username = claims["sub"]
        except (InvalidTokenError, KeyError, TypeError):
            raise HTTPException(401, "Invalid or expired token") from None
        if not isinstance(username, str) or username not in users:
            raise HTTPException(401, "Unknown account")
        return username

    @api.get("/me")
    def my_profile(username: str = Depends(current_user)):
        return {"username": username, "message": "You have access to this route"}

    return api

app = create_app(secret_key=os.environ.get("JWT_SECRET_KEY", ""))
