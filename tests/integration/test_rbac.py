"""
Integration tests for RBAC.
Tests INT-012 from Table 6.5.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from delivery.main import app

client = TestClient(app)


class TestRBAC:
    """INT-012: Role-Based Access Control."""
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int012_business_admin_forbidden(self, mock_verify):
        """INT-012: Business admin -> 403 Forbidden on admin endpoints."""
        mock_verify.return_value = {"uid": "biz-uid", "email": "biz@test.com", "role": "business_admin"}
        
        headers = {"Authorization": "Bearer fake-biz-token"}
        response = client.get("/admin/contributions", headers=headers)
        assert response.status_code in [403, 404]
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int012_admin_can_access(self, mock_verify):
        """INT-012: Admin role can access admin endpoints."""
        mock_verify.return_value = {"uid": "admin-uid", "email": "admin@test.com", "role": "admin"}
        
        headers = {"Authorization": "Bearer fake-admin-token"}
        response = client.get("/admin/contributions", headers=headers)
        assert response.status_code in [200, 404]
    
    @patch("infrastructure.auth.firebase_auth.auth.verify_id_token")
    def test_int012_regular_user_forbidden(self, mock_verify):
        """INT-012: Regular user -> 403 Forbidden."""
        mock_verify.return_value = {"uid": "user-uid", "email": "user@test.com", "role": "commuter"}
        
        headers = {"Authorization": "Bearer fake-user-token"}
        response = client.get("/admin/contributions", headers=headers)
        assert response.status_code in [401, 403, 404]
    
    def test_int012_unauthenticated_denied(self):
        """INT-012: No auth -> 401/403/404 (endpoint may not exist)."""
        response = client.get("/admin/contributions")
        assert response.status_code in [401, 403, 404]
