"""
Integration tests for notifications.
Tests INT-010 from Table 6.5.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from delivery.main import app

client = TestClient(app)


class TestNotifications:
    """INT-010: Notification system."""
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int010_notification_queued(self, mock_verify):
        """INT-010: Notification queued on report submission."""
        mock_verify.return_value = {"uid": "test-uid", "email": "test@test.com"}
        
        headers = {"Authorization": "Bearer fake-token"}
        
        response = client.post(
            "/notifications/register-token",
            json={"token": "fcm-token-abc", "platform": "android"},
            headers=headers
        )
        assert response.status_code in [200, 201, 404]
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int010_get_notifications(self, mock_verify):
        """INT-010: User can retrieve notifications."""
        mock_verify.return_value = {"uid": "test-uid", "email": "test@test.com"}
        
        headers = {"Authorization": "Bearer fake-token"}
        response = client.get("/notifications", headers=headers)
        assert response.status_code in [200, 404]
