from sqlalchemy.orm import Session
from domain.admin_model import Admin
from domain.user_model import User
from sqlalchemy.exc import SQLAlchemyError



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
    
    