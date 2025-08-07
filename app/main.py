from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


wallets = {}

FX_RATES = {
    ("USD", "MXN"): 18.7,
    ("MXN", "USD"): 0.053,
}

class FundPayload(BaseModel):
    currency: str
    amount: float

class ConvertPayload(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class WithdrawPayload(BaseModel):
    currency: str
    amount: float

class FundResult(BaseModel):
    currency: str
    amount_funded: float

def supported_currency(currency: str):
    supported = set()
    for pair in FX_RATES.keys():
        supported.update(pair)
    if currency not in supported:
        raise HTTPException(status_code=400, detail="Currency not supported.")

def check_user_id(user_id):
    if user_id not in wallets:
        print('The user wasnt found.')
        return False, None
    return True, wallets[user_id]
    
@app.post("/wallets/{user_id}/fund", response_model=FundResult)
def fund_wallet(user_id: str, payload: FundPayload):
    currency = payload.currency.upper()
    available_currencies = supported_currency(currency)
    created, user_wallet = check_user_id(user_id)
    if not created:
        print(f"User '{user_id}' not found. Creating new user...")
        wallets[user_id] = {}
        user_wallet = wallets[user_id]
        if currency not in user_wallet:
            user_wallet[currency] = 0.0
        
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="The amount entered is not correct.")

    user_wallet[currency] += payload.amount
    return FundResult(currency=currency, amount_funded=payload.amount)

