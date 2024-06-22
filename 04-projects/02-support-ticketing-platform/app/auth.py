from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from .core import check_password, create_token, current_user, get_db, hash_password
from .models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

@router.post("/register", status_code=201)
def register(data: Credentials, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(email=email, password_hash=hash_password(data.password), role="customer")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}

@router.post("/login")
def login(data: Credentials, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if not user or not check_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid login")
    return {"access_token": create_token(user, request.app.state.jwt_secret), "token_type": "bearer"}

@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}
