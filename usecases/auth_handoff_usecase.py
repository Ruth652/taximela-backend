import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from infrastructure.auth.firebase_auth import create_firebase_custom_token
from repository.auth_handoff_repository import AuthHandoffRepository
from repository.user_repository import UserRepository


class HandoffError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


_HANDOFF_MESSAGES = {
    "handoff_invalid": "This link is invalid.",
    "handoff_expired": "This link has expired.",
    "handoff_used": "This link has already been used.",
}


def _handoff_ttl_seconds() -> int:
    raw = int(os.getenv("HANDOFF_TTL_SECONDS", "120"))
    return min(max(raw, 30), 300)


def mint_handoff_token(
    db: Session,
    firebase_uid: str,
    purpose: str | None = None,
) -> dict:
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Complete mobile sign-in before opening the web portal.",
        )

    ttl = _handoff_ttl_seconds()
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

    repo = AuthHandoffRepository(db)
    repo.create(
        token=token,
        firebase_uid=firebase_uid,
        expires_at=expires_at,
        purpose=purpose,
    )

    return {"handoff_token": token, "expires_in": ttl}


def exchange_handoff_token(db: Session, handoff_token: str) -> dict:
    repo = AuthHandoffRepository(db)
    firebase_uid, error_code = repo.consume(handoff_token)

    if error_code:
        raise HandoffError(
            _HANDOFF_MESSAGES.get(error_code, "This link is invalid."),
            error_code,
        )

    custom_token = create_firebase_custom_token(firebase_uid)

    return {
        "custom_token": custom_token,
        "owner_id": firebase_uid,
    }
