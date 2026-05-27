import secrets

from sqlalchemy.exc import IntegrityError
from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository
from infrastructure.auth.firebase_auth import set_firebase_custom_claims, generate_password_reset_link
from infrastructure.email_service import send_admin_invite_email

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

    # 4️ Create auth identity mapping
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

    # 1. Verify the creator exists and is a super_admin
    creator_user_id = auth_repo.get_user_uuid_by_firebase_uid(creator_firebase_uid)
    if not creator_user_id:
        raise UserNotFoundError()

    if not auth_repo.get_super_admin_uuid_by_firebase_uid([creator_firebase_uid]):
        raise PermissionDeniedError()

    creator_admin_id = auth_repo.get_admin_id_by_user_id(creator_user_id)
    if not creator_admin_id:
        raise PermissionDeniedError()

    # 2. Generate a secure random temporary password (admin will replace via email link)
    temp_password = secrets.token_urlsafe(16)

    # 3. Create the Firebase user with the temp password
    firebase = create_firebase_user(
        email=new_user.email,
        password=temp_password,
        display_name=new_user.full_name
    )

    # 4. Set the admin role as a custom claim on the Firebase token
    set_firebase_custom_claims(firebase.uid, {"role": new_user.role.value})

    # 5. Generate a password-reset link so the admin can set their own password
    reset_link = generate_password_reset_link(new_user.email)

    # 6. Create the user record in the main DB
    user = user_repo.create_user(
        email=new_user.email,
        full_name=new_user.full_name,
        preferred_language="en",
    )

    # 7. Map Firebase UID → internal user ID
    auth_repo.create_auth_identity(
        firebase_uid=firebase.uid,
        entity_type="admin",
        entity_id=user.id
    )

    # 8. Promote the user to admin with the specified role
    user_repo.promote_to_admin(
        user.id,
        role=new_user.role,
        created_by=creator_admin_id
    )

    db.commit()

    # 9. Send the branded invitation email with the password-setup link
    send_admin_invite_email(
        to=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role.value,
        reset_link=reset_link,
    )

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


def update_current_user(db, firebase_uid: str, payload):
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

    raw = payload.dict() if hasattr(payload, "dict") else dict(payload)

    update_data = {
        key: value
        for key, value in raw.items()
        if key in allowed_fields and value is not None
    }

    if not update_data:
        raise NoUpdateFieldsError()

    return user_repo.update_user_profile(user_id, update_data)
