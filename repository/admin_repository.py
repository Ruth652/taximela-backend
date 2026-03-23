from sqlalchemy.orm import Session
from domain.admin_model import Admin
from domain.user_model import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from domain.auth_identity_model import AuthIdentity




class AdminRepository:
    def __init__(self, db: Session):
        self.db = db
    

    def get_admin_by_id(self, admin_id):
         return self.db.query(Admin).filter(Admin.id == admin_id).first()

   
    def create_admin(self, user_id, role, created_by):
        admin = Admin(
            user_id = user_id,
            role = role,
            created_by = created_by
        )

        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin
    
    def update_admin(self, admin_id, payload):
        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None
        try:
            if getattr(payload, "role", None) is not None:
                admin.role = payload.role
            if getattr(payload, "is_active", None) is not None:
                admin.is_active = payload.is_active
            self.db.commit()
            self.db.refresh(admin)
            
            return admin
            
        except SQLAlchemyError:
            self.db.rollback()
            raise
        
    def delete_admin(self, admin_id):
        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None
        try:
            admin.is_active = False
            
            self.db.commit()
            return admin
        except SQLAlchemyError:
            self.db.rollback()
            raise
    def get_admin_by_firebase_uid(self, firebase_uid: str):
        return (
            self.db.query(Admin)
            .join(User, Admin.user_id == User.id)
            .join(AuthIdentity, and_(
                AuthIdentity.entity_id == User.id,
                AuthIdentity.entity_type == "admin"
            ))
            .filter(AuthIdentity.firebase_uid == firebase_uid)
            .first()
        )

    def list_admins(self, page: int = 1, limit: int = 20, status: str = None, roles=None):
        query = (
            self.db.query(Admin, User, AuthIdentity.firebase_uid)
            .join(User, Admin.user_id == User.id)
            .outerjoin(AuthIdentity, and_(
                AuthIdentity.entity_id == User.id,
                AuthIdentity.entity_type == "admin"
            ))
        )

        if status:
            query = query.filter(User.status == status)

        if roles:
            query = query.filter(Admin.role.in_(roles))
        else:
            query = query.filter(Admin.role.in_(["business_admin", "operational_admin", "super_admin"]))

        total_count = query.count()
        offset = (page - 1) * limit
        rows = query.offset(offset).limit(limit).all()

        admins = []
        for admin, user, firebase_uid in rows:
            admins.append({
                "admin_id": str(admin.id),
                "role": admin.role,
                "is_active": admin.is_active,
                "created_at": admin.created_at,
                "user": {
                    "id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "status": user.status,
                    "profile_picture_url": user.profile_picture_url,
                    "created_at": user.created_at,
                },
                "firebase_uid": firebase_uid
            })
        print("Admins fetched:", admins)
        return {
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "admins": admins
        }
    