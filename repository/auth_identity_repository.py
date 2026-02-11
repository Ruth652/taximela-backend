from sqlalchemy.orm import Session
from domain.auth_identity_model import AuthIdentity

class AuthIdentityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_uuid_by_firebase_uid(self, firebase_uid: str):
        """
        Return internal users.id (UUID) as a string for the given firebase_uid,
        or None if not found.
        """
        record = self.db.query(AuthIdentity).filter(AuthIdentity.firebase_uid == firebase_uid).first()
        return str(record.entity_id) if record and record.entity_id else None
