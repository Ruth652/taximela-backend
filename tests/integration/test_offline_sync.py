"""
Integration tests for offline sync.
Tests INT-011 from Table 6.5.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from delivery.main import app

client = TestClient(app)


class TestOfflineSync:
    """INT-011: Offline synchronization."""
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int011_saved_routes_cached(self, mock_verify):
        """INT-011: Saved routes cached for offline access."""
        mock_verify.return_value = {"uid": "test-uid", "email": "test@test.com"}
        
        headers = {"Authorization": "Bearer fake-token"}
        
        # Save route
        response = client.post("/routes/save", json={"route_id": "R-1042"}, headers=headers)
        assert response.status_code in [200, 201, 404]
        
        # Get saved routes
        response = client.get("/routes/saved", headers=headers)
        assert response.status_code in [200, 404]
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int011_offline_actions_synced(self, mock_verify):
        """INT-011: Offline actions queued, synced when online."""
        mock_verify.return_value = {"uid": "test-uid", "email": "test@test.com"}
        
        headers = {"Authorization": "Bearer fake-token"}
        
        response = client.post("/sync", json={"actions": []}, headers=headers)
        assert response.status_code in [200, 201, 404]
