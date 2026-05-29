from sqlalchemy.exc import IntegrityError
from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository
from uuid import uuid4
from infrastructure.config.supabase_client import supabase

class UserNotFoundError(Exception): pass
class NoUpdateFieldsError(Exception): pass
class PermissionDeniedError(Exception): pass



def create_user_first_login(
    db,
    firebase_uid: str,
    email: str,
    payload: dict | None = None,
    *,
    entity_type: str = "user"
):

    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    payload = payload or {}

    # 1️⃣ Check if Firebase identity already exists
    existing_user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)

    if existing_user_id:
        user = user_repo.get_user_by_id(existing_user_id)

        return {
            "id": user.id,
            "firebase_uid": firebase_uid,
            "email": user.email,
            "full_name": user.full_name,
        }

    # 2️ Check if user exists by email
    print("# 2 Check if user exists by email")
    user = user_repo.get_user_by_email(email)

    # 3️ If user does not exist → create user
    if not user:
        print("# 3 If user does not exist → create user")

        user = user_repo.create_user(
            email=email,
            full_name=payload.get("full_name"),
            preferred_language=payload.get("preferred_language", "en"),
            is_commuter=payload.get("is_commuter", False),
            is_business_owner=payload.get("is_business_owner", False),
        )

    user_id = user.id

    
    auth_repo.create_auth_identity(
        firebase_uid=firebase_uid,
        entity_id=user_id,
        entity_type=entity_type
    )

    return {
        "id": user_id,
        "firebase_uid": firebase_uid,
        "email": user.email,
        "full_name": user.full_name,
    }

def create_admin_first_login(
    db,
    creator_firebase_uid: str,
    new_user,
    create_firebase_user
):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    creator_user_id = auth_repo.get_user_uuid_by_firebase_uid(creator_firebase_uid)
    if not creator_user_id:
        raise UserNotFoundError()

    if not auth_repo.get_super_admin_uuid_by_firebase_uid([creator_firebase_uid]):
        raise PermissionDeniedError()
    
    creator_admin_id = auth_repo.get_admin_id_by_user_id(creator_user_id)
    if not creator_admin_id:
        raise PermissionDeniedError()
    
    firebase = create_firebase_user(
        email=new_user.email,
        password="DefaultPassword123!",  
        display_name=new_user.full_name
    ) 
    user = user_repo.create_user(
        email=new_user.email,
        full_name=new_user.full_name,
        preferred_language="en",
    )
    auth_repo.create_auth_identity(
        firebase_uid=firebase.uid,
        entity_type="admin",
        entity_id=user.id 
    )
        
    user_repo.promote_to_admin(
        user.id,
        role=new_user.role,
        created_by=creator_admin_id
    )
        
    db.commit()

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": new_user.role
    }
    

def get_current_user(db, firebase_uid: str):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        return None

    return user_repo.get_user_by_id(user_id)


async def update_current_user(
    db,
    firebase_uid: str,
    full_name=None,
    preferred_language=None,
    profile_picture=None
):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)

    if not user_id:
        raise UserNotFoundError()

    update_data = {}

    if full_name is not None:
        update_data["full_name"] = full_name

    if preferred_language is not None:
        update_data["preferred_language"] = preferred_language

   
    if profile_picture is not None:

        file_bytes = await profile_picture.read()

        file_name = f"{user_id}-{uuid4()}.png"

        supabase.storage.from_("profile-pictures").upload(
            path=file_name,
            file=file_bytes,
            file_options={
                "content-type": profile_picture.content_type
            }
        )

        image_url = supabase.storage.from_(
            "profile-pictures"
        ).get_public_url(file_name)

        update_data["profile_picture_url"] = image_url

    if not update_data:
        raise NoUpdateFieldsError()

    return user_repo.update_user_profile(user_id, update_data)