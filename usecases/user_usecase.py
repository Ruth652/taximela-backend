from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository

class UserNotFoundError(Exception): pass
class NoUpdateFieldsError(Exception): pass

def create_user_first_login(db, firebase_uid, email, payload: dict | None):
    # check if firebase id exists in auth_identity and return existing user
    # check if email exists in users table and return
    # else create user 
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    existing_user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if existing_user_id:
        user = user_repo.get_user_by_id(existing_user_id)
        return {
           
        "id": user.id,
        "firebase_uid": firebase_uid,
        "email": user.email,
        "full_name": user.full_name,
        }


    # 2. Check user by email
    user = user_repo.get_user_by_email(email)

    if not user:
        user = user_repo.create_user(
            email=email,
            full_name=payload.get("full_name") if payload else None,
            preferred_language=payload.get("preferred_language") if payload else "en"
        )

    # 3. Link firebase UID
    auth_repo.create_auth_identity(
        firebase_uid=firebase_uid,
        entity_id=user.id
    )

    return {
           
        "id": user.id,
        "firebase_uid": firebase_uid,
        "email": user.email,
        "full_name": user.full_name,
        
    }

def get_current_user(db, firebase_uid: str):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        return None
    
    return user_repo.get_user_by_id(user_id)

def update_current_user(db, firebase_uid: str, payload: dict):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        raise UserNotFoundError()

    allowed_fields = {
        "full_name",
        "preferred_language",
        "profile_picture_url"
    }

    update_data = {
        key: value
        for key, value in payload.dict().items()
        if key in allowed_fields and value is not None
    }

    if not update_data:
        raise NoUpdateFieldsError()

        
    return user_repo.update_user_profile(user_id, update_data)
    
    
