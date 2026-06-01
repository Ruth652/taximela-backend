"""
Auth handoff unit tests. Run: pytest tests/test_auth_handoff.py -v
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from domain.auth_handoff_model import AuthHandoffToken
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from delivery.api.routers.auth_handoff_router import router as auth_handoff_router
from usecases.auth_handoff_usecase import HandoffError, exchange_handoff_token, mint_handoff_token


@pytest.fixture
def handoff_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    AuthHandoffToken.__table__.create(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def test_mint_requires_local_user(handoff_db):
    with patch("usecases.auth_handoff_usecase.UserRepository") as repo_cls:
        repo_cls.return_value.get_user_by_firebase_uid.return_value = None
        with pytest.raises(Exception) as exc:
            mint_handoff_token(handoff_db, "uid-missing")
        assert exc.value.status_code == 404


def test_mint_and_exchange_roundtrip(handoff_db):
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()

    with patch("usecases.auth_handoff_usecase.UserRepository") as repo_cls:
        repo_cls.return_value.get_user_by_firebase_uid.return_value = mock_user

        minted = mint_handoff_token(handoff_db, "firebase-uid-1", purpose="business_owner_web")
        assert minted["expires_in"] == 120
        assert len(minted["handoff_token"]) > 20

    with patch(
        "usecases.auth_handoff_usecase.create_firebase_custom_token",
        return_value="custom-token-abc",
    ):
        result = exchange_handoff_token(handoff_db, minted["handoff_token"])
        assert result["custom_token"] == "custom-token-abc"
        assert result["owner_id"] == "firebase-uid-1"

    with pytest.raises(HandoffError) as exc:
        exchange_handoff_token(handoff_db, minted["handoff_token"])
    assert exc.value.code == "handoff_used"


def test_exchange_invalid(handoff_db):
    with pytest.raises(HandoffError) as exc:
        exchange_handoff_token(handoff_db, "does-not-exist")
    assert exc.value.code == "handoff_invalid"


def test_exchange_expired(handoff_db):
    from repository.auth_handoff_repository import AuthHandoffRepository

    repo = AuthHandoffRepository(handoff_db)
    token = "expired-token-xyz"
    repo.create(
        token=token,
        firebase_uid="firebase-uid-1",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=30),
    )

    with pytest.raises(HandoffError) as exc:
        exchange_handoff_token(handoff_db, token)
    assert exc.value.code == "handoff_expired"


def test_http_exchange_error_shape():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    AuthHandoffToken.__table__.create(bind=engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(auth_handoff_router)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        resp = client.post(
            "/api/auth/handoff/exchange",
            json={"handoff_token": "bad-token"},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == "handoff_invalid"
        assert "message" in body


def test_mint_without_auth_returns_401_or_403():
    app = FastAPI()
    app.include_router(auth_handoff_router)

    with TestClient(app) as client:
        resp = client.post("/api/auth/handoff", json={})
        assert resp.status_code in (401, 403)
