import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fund_wallet():
    user_id = "user123"

    response = client.post(f"/wallets/{user_id}/fund", json={"currency": "USD", "amount": 1000})
    assert response.status_code == 200
    data = response.json()
    assert "USD" in data
    assert data["USD"] == 1000

def test_convert_currency():
    user_id = "user2"

    client.post(f"/wallets/{user_id}/fund", json={"currency": "USD", "amount": 1000})
    
    response = client.post(f"/wallets/{user_id}/convert", json={
        "from_currency": "USD",
        "to_currency": "MXN",
        "amount": 500
    })

    assert response.status_code == 200
    data = response.json()
    assert data["USD"] == 500
    assert abs(data["MXN"] - 9350) < 0.01

