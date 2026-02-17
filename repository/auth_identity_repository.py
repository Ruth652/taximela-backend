from sqlalchemy.orm import Session
from domain.admin_model import Admin
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
        return record.entity_id if record else None

    def create_auth_identity(self, firebase_uid, entity_id):
        record = AuthIdentity(
            firebase_uid=firebase_uid,
            entity_id=entity_id
        )
        self.db.add(record)
        self.db.commit()
    def get_admin_uuids(self, firebase_uids: list[str] = None):
        query = self.db.query(AuthIdentity.entity_id).filter(AuthIdentity.entity_type == "admin")
        if firebase_uids:
            query = query.filter(AuthIdentity.firebase_uid.in_(firebase_uids))
        return set(record.entity_id for record in query.all())


    def get_operational_admin_uuids(self, firebase_uids: list[str] = None):
        admins = self.get_admin_uuids(firebase_uids)
        
        if not admins:
            return set()
        
        if admins:
            query = self.db.query(Admin.user_id).filter(
                Admin.user_id.in_(admins),
                Admin.role.in_(["operational_admin", "super_admin"])
            )
            return set(record.user_id for record in query.all())
           