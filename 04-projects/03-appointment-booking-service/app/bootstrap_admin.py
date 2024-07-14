"""Interactive bootstrap for local demos. Run: python -m app.bootstrap_admin"""
import getpass
import os
from sqlalchemy import select
from .core import configure_database, hash_password, settings
from .models import User
from fastapi import FastAPI

def main():
    url, _ = settings()
    app = FastAPI()
    configure_database(app, url)
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password (min 8 chars): ")
    if "@" not in email or len(password) < 8:
        raise SystemExit("Provide a valid email and password of at least 8 characters")
    with app.state.session_factory() as db:
        if db.scalar(select(User).where(User.email == email)):
            raise SystemExit("Account already exists; no roles changed")
        db.add(User(email=email, password_hash=hash_password(password), role="admin"))
        db.commit()
    print("Admin created. Remove this bootstrap access in deployed environments.")

if __name__ == "__main__":
    main()
