"""A small registration/login API. Storage is in memory for this example."""
import hashlib
import hmac
import secrets
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

class Credentials(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=8, max_length=128)

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}:{digest.hex()}"

def password_matches(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split(":", maxsplit=1)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
    return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))

def create_app() -> FastAPI:
    api = FastAPI(title="Registration and Login Example")
    users: dict[str, str] = {}

    @api.post("/users/register", status_code=status.HTTP_201_CREATED)
    def register(data: Credentials):
        email = data.email.strip().lower()
        if email in users:
            raise HTTPException(409, detail="Email already registered")
        users[email] = hash_password(data.password)
        return {"email": email, "message": "Account created"}

    @api.post("/users/login")
    def login(data: Credentials):
        email = data.email.strip().lower()
        saved = users.get(email)
        if not saved or not password_matches(data.password, saved):
            raise HTTPException(401, detail="Invalid email or password")
        return {"email": email, "message": "Login successful (no session issued in this example)"}

    return api

app = create_app()
