from datetime import datetime

from sqlalchemy.orm import Session
from domain.admin_model import Admin
from domain.auth_identity_model import AuthIdentity
from domain.user_model import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from datetime import date



class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email, full_name=None, preferred_language="en", is_commuter=False, is_business_owner=False, fcm_token=None):
        user = User(
            email=email,
            full_name=full_name,
            preferred_language=preferred_language,
            is_commuter=is_commuter,
            is_business_owner=is_business_owner,
            rating_score=20,
            last_active_date=date.today(),
            fcm_token=fcm_token,
        )
        self.db.add(user)
        self.db.commit()
        return user
    def get_user_by_id(self,user_id):
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return None
        
        return user
    
    def get_user_by_firebase_uid(self, firebase_uid: str):
        return (
            self.db.query(User)
            .join(AuthIdentity, and_(
                AuthIdentity.entity_id == User.id,
                AuthIdentity.entity_type == "user"
            ))
            .filter(AuthIdentity.firebase_uid == firebase_uid)
            .first()
        )

    def update_user_profile(self, user_id, update_data: dict):
        from usecases.user_usecase import UserNotFoundError
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()

        try:
            for key, value in update_data.items():
                setattr(user, key, value)

            self.db.commit()
            self.db.refresh(user)
            return user
        except SQLAlchemyError:
            self.db.rollback()
            raise 


    def list_users(self, page: int=1, limit: int =20, status: str=None):
        query = self.db.query(User)



        if status: 
            query =query.filter(User.status ==status)
        total_count= query.count()    
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()

        return {
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "users": users
        }

    def update_user_status(self,user_id, new_status: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.status = new_status
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def promote_to_admin(self, user_id, role: str, created_by: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        admin = Admin(
            user_id=user_id,
            role=role,
            created_by=created_by,
            is_active=True 
            )
            

        self.db.add(admin)
        self.db.flush()
     
        return admin
    
    def delete_user(self, user_id):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.status = "suspended"
        user.deleted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    def promote_to_business_owner(self, user):
        try:
            user.is_business_owner = True
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            print(f"--- [UserRepository] Error updating user: {e} ---")
            raise e
    def update_daily_activity(self, user):

        user.last_active_date = date.today()

        self.db.commit()
        self.db.refresh(user)

        return user
    def update_user_navigation_done(self, user):
        user.rating_score += 2
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_fcm_token(self, user_id, fcm_token: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.fcm_token = fcm_token
        self.db.commit()
        self.db.refresh(user)
        return user