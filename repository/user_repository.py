from sqlalchemy.orm import Session
from domain.user_model import User
from sqlalchemy.exc import SQLAlchemyError

from usecases.user_usecase import UserNotFoundError


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    

    def get_user_by_id(self, user_id):
         return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email, full_name=None, preferred_language="en"):
        user = User(
            email= email,
            full_name = full_name,
            preferred_language = preferred_language,

        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    def get_user_by_id(self,user_id):
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return None
        
        return user
    def update_user_profile(self, user_id, update_data):
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
            raise UserUpdateFailedError()


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
            

       