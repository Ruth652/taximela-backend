import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from delivery.main import app  

client = TestClient(app)


# @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
@patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
def test_valid_firebase_token(mock_verify):

    mock_verify.return_value = {
        "uid": "test-uid-123",
        "email": "test@test.com"
    }

    payload = {
        "from_lat": 9.03,
        "from_lon": 38.74,
        "to_lat": 9.01,
        "to_lon": 38.76
    }

    headers = {
        "Authorization": "Bearer fake-valid-token"
    }

    response = client.post("/routes/plan", json=payload, headers=headers)

    assert response.status_code in [200, 500]


@patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
def test_invalid_firebase_token(mock_verify):

    mock_verify.side_effect = Exception("Invalid token")

    payload = {
        "from_lat": 9.03,
        "from_lon": 38.74,
        "to_lat": 9.01,
        "to_lon": 38.76
    }

    headers = {
        "Authorization": "Bearer invalid-token"
    }

    response = client.post("/routes/plan", json=payload, headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_missing_token():

    payload = {
        "from_lat": 9.03,
        "from_lon": 38.74,
        "to_lat": 9.01,
        "to_lon": 38.76
    }

    response = client.post("/routes/plan", json=payload)

    assert response.status_code in [401, 403]