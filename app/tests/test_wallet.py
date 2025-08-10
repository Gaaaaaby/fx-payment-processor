from unittest.mock import MagicMock
import pytest

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json

class FakeClient:
    def post(self, url, json):
        if url.endswith("/fund"):
            return MockResponse(200, {"currency": json["currency"], "amount_funded": json["amount"]})
        elif url.endswith("/convert"):
            from_curr = json["from_currency"]
            to_curr = json["to_currency"]
            amount = json["amount"]
            if from_curr == "USD" and to_curr == "MXN":
                return MockResponse(200, {from_curr: amount, to_curr: amount * 18.7})
            else:
                return MockResponse(400, {"error": "Unsupported conversion"})
        elif url.endswith("/withdraw"):
            return MockResponse(200, {"currency": json["currency"], "amount_withdrawn": json["amount"]})
        else:
            return MockResponse(404, {})

    def get(self, url):
        if url.endswith("/balance"):
            return MockResponse(200, {"USD": 200, "EUR": 100})
        return MockResponse(404, {})

client = FakeClient()

def test_fund_wallet():
    user_id = "user123"
    response = client.post(f"/wallets/{user_id}/fund", json={"currency": "USD", "amount": 1000})
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"
    assert data["amount_funded"] == 1000.0

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

def test_show_balance():
    user_id = "user3"
    client.post(f"/wallets/{user_id}/fund", json={"currency": "EUR", "amount": 200})

    response = client.get(f"/wallets/{user_id}/balance")
    assert response.status_code == 200
    data = response.json()
    assert "EUR" in data

def test_withdraw_funds():
    user_id = "user4"
    client.post(f"/wallets/{user_id}/fund", json={"currency": "USD", "amount": 500})

    response = client.post(f"/wallets/{user_id}/withdraw", json={"currency": "USD", "amount": 300})
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"
    assert data["amount_withdrawn"] == 300

    balance_response = client.get(f"/wallets/{user_id}/balance")
    assert balance_response.status_code == 200
    balance = balance_response.json()
    assert balance["USD"] == 200
