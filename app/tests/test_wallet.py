# import pytest
# from fastapi.testclient import TestClient
# from main import app

# client = TestClient(app)


# user_id = "gabriela_test"
# currency = "USD"
# initial_amount = 100.0
# withdraw_amount = 50.0
# invalid_amount = -10.0

# def test_fund_valid():
#     response = client.post("/fund", json={
#         "user_id": user_id,
#         "currency": currency,
#         "amount": initial_amount
#     })
#     assert response.status_code == 200
#     assert "Deposit successful" in response.json().get("message", "")

# def test_fund_invalid_amount():
#     response = client.post("/fund", json={
#         "user_id": user_id,
#         "currency": currency,
#         "amount": invalid_amount
#     })
#     assert response.status_code == 400

# def test_withdraw_valid():
#     response = client.post("/withdraw", json={
#         "user_id": user_id,
#         "currency": currency,
#         "amount": withdraw_amount
#     })
#     assert response.status_code == 200
#     assert "Withdrawal successful" in response.json().get("message", "")

# def test_withdraw_insufficient_funds():
#     response = client.post("/withdraw", json={
#         "user_id": user_id,
#         "currency": currency,
#         "amount": 9999.0  # Excesivo
#     })
#     assert response.status_code == 400

# def test_balances():
#     response = client.get(f"/balances?user_id={user_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, dict)
#     assert currency in data
#     assert data[currency] >= 0