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
    
    