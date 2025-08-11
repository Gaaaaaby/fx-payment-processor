
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "sqlite:///./wallets.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    currency = Column(String)
    balance = Column(Float, default=0.0)
    user = relationship("User", back_populates="wallets")
    __table_args__ = (UniqueConstraint('user_id', 'currency', name='_user_currency_uc'),)

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    currency_from = Column(String(3), index=True, nullable=False)
    currency_to = Column(String(3), index=True, nullable=False)
    rate = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("currency_from", "currency_to", name="_currency_pair_uc"),)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BaseTransactionPayload(BaseModel):
    currency: str
    amount: float

class FundPayload(BaseModel):
    pass

class ConvertPayload(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class WithdrawPayload(BaseTransactionPayload):
    wallet_id: str

class BaseTransactionResult(BaseModel):
    currency: str
    amount: float

class FundResult(BaseModel):
    currency: str
    amount_funded: float

class BalanceResult(BaseModel):
    user_id: str
    balance: float

class WithdrawResult(BaseModel):
    balance: float
    amount: float
    wallet_id: str

class ConvertResult(BaseModel):
    user_id: str
    wallet_id: str
    from_currency: str
    to_currency: str


@app.get("/users/{user_id}", status_code=201)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"The User {user_id} wasnt found.")

@app.post("/wallets/{user_id}/fund", response_model=FundResult)
def fund_wallet(user_id: str, payload: FundPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"The User {user_id} wasnt found.")
    
    currency = payload.currency.upper()
    currency_result = db.query(ExchangeRate).filter(ExchangeRate.currency_from == currency).all()
    if not currency_result:
        raise HTTPException(status_code=400, detail=f"The currency isnt available")
    
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="The amount entered is not correct.")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id, Wallet.currency == currency).first()
    if wallet:
        wallet.balance += payload.amount
    else:
        
        wallet = Wallet(user_id=user_id, currency=currency, balance=payload.amount)
        db.add(wallet)

    db.commit()
    db.refresh(wallet)
    return FundResult(currency=currency, amount_funded=payload.amount)

@app.post("/wallets/{user_id}/convert")
def convert(user_id: str, wallet_id: int, payload: ConvertPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"The User {user_id} wasn't found.")
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id, Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=400, detail=f"The Wallet with the id {wallet_id} for user {user_id} not found.")
    
    from_curr = payload.from_currency.upper()
    to_curr = payload.to_currency.upper()
    amount = payload.amount
    if from_curr not in wallet.balance or wallet.balance[from_curr] < amount:
        raise HTTPException(status_code=400, detail=f"Insufficient funds in {from_curr}")

    if to_curr not in wallet.balance:
        raise HTTPException(status_code=400,detail=f"{to_curr} is not supported in this wallet")

    exchange_rate = db.query(ExchangeRate).filter(
        ExchangeRate.currency_from == from_curr,
        ExchangeRate.currency_to == to_curr
    ).first()

    if not exchange_rate:
        raise HTTPException(status_code=400, detail=f"No exchange rate found for {from_curr} to {to_curr}")

    converted_amount = round(amount * exchange_rate.rate, 2)

    wallet.balance[from_curr] -= amount
    wallet.balance[to_curr] = wallet.balance.get(to_curr, 0) + converted_amount

    db.commit()

    return ConvertResult(user_id=user_id, wallet_id=wallet_id, from_currency=payload.from_currency, to_currency=payload.to_currency)
    

@app.post("/wallets/{user_id}/withdraw")
def withdraw(user_id: str, payload: WithdrawPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"The User {user_id} wasnt found.")
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id, Wallet.id == payload.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=400, detail=f"The Wallet with the id {payload.wallet_id} from user {user_id} not found.")
    
    curr = payload.currency.upper()
    amount = payload.amount

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    wallet.balance -= amount
    db.commit()
    db.refresh(wallet)
    return WithdrawResult(balance=wallet.balance,amount=payload.amount, wallet_id=payload.wallet_id)


@app.get("/wallets/{user_id}/balances")
def get_balances(user_id: str, wallet_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"The User {user_id} wasnt found.")
    else:
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id, Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=400, detail=f"The Wallet with the id {wallet_id} for user {user_id} not found.")
        
    return BalanceResult(user_id=user_id, wallet_id=wallet_id, balance=wallet.balance)

