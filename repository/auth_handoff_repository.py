from datetime import datetime, timezone

from sqlalchemy.orm import Session

from domain.auth_handoff_model import AuthHandoffToken


class AuthHandoffRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        token: str,
        firebase_uid: str,
        expires_at: datetime,
        purpose: str | None = None,
    ) -> AuthHandoffToken:
        row = AuthHandoffToken(
            token=token,
            firebase_uid=firebase_uid,
            purpose=purpose,
            expires_at=expires_at,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def consume(self, token: str) -> tuple[str | None, str | None]:
        """
        Atomically validate and mark token used.
        Returns (firebase_uid, None) on success.
        Returns (None, error_code) on failure.
        """
        row = (
            self.db.query(AuthHandoffToken)
            .filter(AuthHandoffToken.token == token)
            .with_for_update()
            .first()
        )
        if not row:
            return None, "handoff_invalid"

        now = datetime.now(timezone.utc)
        expires = row.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if row.used_at is not None:
            self.db.rollback()
            return None, "handoff_used"

        if expires <= now:
            self.db.rollback()
            return None, "handoff_expired"

        row.used_at = now
        self.db.commit()
        return row.firebase_uid, None

    def delete_expired_before(self, cutoff: datetime) -> int:
        deleted = (
            self.db.query(AuthHandoffToken)
            .filter(AuthHandoffToken.expires_at < cutoff)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted
