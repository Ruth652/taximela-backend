from sqlalchemy.orm import Session
from domain.user_model import User
from sqlalchemy.exc import SQLAlchemyError



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
            raise UserUpdateFailedError()