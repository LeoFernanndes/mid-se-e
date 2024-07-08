from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_reset_state():
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.content.decode() == "OK"


def test_get_balance_for_non_existent_account():
    response = client.get("/balance?account_id=1234")
    assert response.status_code == 404
    assert response.content.decode() == "0"


def test_create_account_with_initial_balance():
    payload = {
        "type": "deposit",
        "destination": "100",
        "amount": 10
    }
    response = client.post("/event", json=payload)

    expected_response_content = {
        "destination": {
            "id": "100",
            "balance": 10
        }
    }
    assert response.status_code == 201
    assert response.json() == expected_response_content


def test_deposit_into_existing_account():
    payload = {
        "type": "deposit",
        "destination": "100",
        "amount": 10
    }
    response = client.post("/event", json=payload)

    expected_response = {
        "destination": {
            "id": "100",
            "balance": 20
        }
    }
    assert response.status_code == 201
    assert response.json() == expected_response


def test_get_balance_for_existing_account():
    response = client.get("/balance?account_id=100")
    assert response.status_code == 200
    assert response.content.decode() == "20"


def test_withdraw_from_non_existing_account():
    payload = {
        "type": "withdraw",
        "origin": "200",
        "amount": 10
    }
    response = client.post("/event", json=payload)
    assert response.status_code == 404
    assert response.content.decode() == "0"


def test_withdraw_from_existing_account():
    payload = {
        "type": "withdraw",
        "origin": "100",
        "amount": 5
    }
    response = client.post("/event", json=payload)
    expected_response = {
        "origin": {
            "id": "100",
            "balance": 15
        }
    }
    assert response.status_code == 201
    assert response.json() == expected_response


def test_transfer_from_existing_account():
    payload = {
        "type": "transfer",
        "origin": "100",
        "amount": 15,
        "destination": "300"
    }
    response = client.post("/event", json=payload)
    expected_response = {
        "origin": {
            "id": "100",
            "balance": 0
        },
        "destination": {
            "id": "300",
            "balance": 15
        }
    }
    assert response.status_code == 201
    assert response.json() == expected_response


def test_transfer_from_non_existing_account():
    payload = {
        "type": "transfer",
        "origin": "200",
        "amount": 15,
        "destination": "300"
    }
    response = client.post("/event", json=payload)
    assert response.status_code == 404
    assert response.content.decode() == "0"
