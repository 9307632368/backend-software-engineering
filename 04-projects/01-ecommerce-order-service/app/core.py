import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, User

bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260_000)
    return "pbkdf2_sha256$260000$" + salt.hex() + "$" + digest.hex()

def check_password(password: str, stored: str) -> bool:
    try:
        scheme, rounds, salt, digest = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        guess = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(guess, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False

def create_token(user: User, key: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=4)}, key, algorithm="HS256")

def configure_database(app, url: str):
    args = {"check_same_thread": False, "timeout": 15} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=args)
    Base.metadata.create_all(engine)  # demo setup; for production use migrations
    app.state.engine = engine
    app.state.session_factory = sessionmaker(engine, expire_on_commit=False)

def get_db(request: Request):
    with request.app.state.session_factory() as session:
        yield session

def current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, request.app.state.jwt_secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(401, "Account no longer exists")
    return user

def require_role(user: User, *roles: str):
    if user.role not in roles:
        raise HTTPException(403, "Insufficient permissions")

def settings(database_url=None, jwt_secret=None):
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./app.db")
    secret = jwt_secret or os.getenv("JWT_SECRET", "local-demo-only-change-before-deploy")
    if len(secret) < 24:
        raise ValueError("JWT_SECRET must be at least 24 characters")
    return url, secret
