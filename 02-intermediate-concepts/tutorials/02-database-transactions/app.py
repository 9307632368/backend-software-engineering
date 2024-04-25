"""SQLAlchemy session per request; atomic wallet transfers (no real money)."""
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner: Mapped[str] = mapped_column(String(70), unique=True)
    balance_paise: Mapped[int] = mapped_column(Integer, default=0)

class CreateWallet(BaseModel):
    owner: str = Field(min_length=2, max_length=70)
    initial_paise: int = Field(ge=0, le=10_000_000)

class Transfer(BaseModel):
    from_id: int
    to_id: int
    amount_paise: int = Field(gt=0)

def create_app(url='sqlite:///./wallets.db'):
    engine = create_engine(url, connect_args={'check_same_thread': False} if url.startswith('sqlite') else {})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    app = FastAPI(title='2024 — SQLAlchemy Transactions')

    def get_db():
        with SessionLocal() as session:
            yield session

    @app.post('/wallets', status_code=201)
    def add_wallet(payload: CreateWallet, db: Session = Depends(get_db)):
        if db.scalar(select(Wallet).where(Wallet.owner == payload.owner)):
            raise HTTPException(409, 'Owner already exists')
        wallet = Wallet(owner=payload.owner, balance_paise=payload.initial_paise)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return {'id': wallet.id, 'owner': wallet.owner, 'balance_paise':wallet.balance_paise}

    @app.get('/wallets/{wallet_id}')
    def read_wallet(wallet_id: int, db: Session = Depends(get_db)):
        wallet = db.get(Wallet, wallet_id)
        if wallet is None: raise HTTPException(404, 'Wallet not found')
        return {'id':wallet.id, 'owner':wallet.owner, 'balance_paise':wallet.balance_paise}

    @app.post('/transfers')
    def transfer(payload: Transfer, db: Session = Depends(get_db)):
        if payload.from_id == payload.to_id: raise HTTPException(400,'Wallets must differ')
        sender = db.get(Wallet, payload.from_id)
        receiver = db.get(Wallet, payload.to_id)
        if sender is None or receiver is None: raise HTTPException(404, 'Wallet missing')
        if sender.balance_paise < payload.amount_paise: raise HTTPException(409, 'Insufficient balance')
        sender.balance_paise -= payload.amount_paise
        receiver.balance_paise += payload.amount_paise
        db.commit()  # both changes in one transaction
        return {'from_balance_paise':sender.balance_paise, 'to_balance_paise':receiver.balance_paise}

    return app

app = create_app()
