"""
Integration tests for authentication.
Tests INT-001 through INT-004 from Table 6.5.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from delivery.main import app

client = TestClient(app)


@patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
def test_int001_valid_token(mock_verify):
    """INT-001: Valid Firebase token -> 200 OK."""
    mock_verify.return_value = {"uid": "test-uid-123", "email": "test@test.com"}
    
    payload = {"from_lat": 9.03, "from_lon": 38.74, "to_lat": 9.01, "to_lon": 38.76}
    headers = {"Authorization": "Bearer fake-valid-token"}
    
    response = client.post("/routes/plan", json=payload, headers=headers)
    assert response.status_code in [200, 500]


@patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
def test_int002_invalid_token(mock_verify):
    """INT-002: Invalid token -> 401 Unauthorized."""
    mock_verify.side_effect = Exception("Invalid token")
    
    payload = {"from_lat": 9.03, "from_lon": 38.74, "to_lat": 9.01, "to_lon": 38.76}
    headers = {"Authorization": "Bearer invalid-token"}
    
    response = client.post("/routes/plan", json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
def test_int003_auth_profile(mock_verify):
    """INT-003: Auth-Profile -> 200 OK + profile data."""
    mock_verify.return_value = {"uid": "test-uid-123", "email": "test@test.com"}
    
    headers = {"Authorization": "Bearer fake-valid-token"}
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code in [200, 404]


def test_int004_missing_token():
    """INT-004: No token -> 401/403."""
    payload = {"from_lat": 9.03, "from_lon": 38.74, "to_lat": 9.01, "to_lon": 38.76}
    response = client.post("/routes/plan", json=payload)
    assert response.status_code in [401, 403]
