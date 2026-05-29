from sqlalchemy.exc import IntegrityError
from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository

class UserNotFoundError(Exception): pass
class NoUpdateFieldsError(Exception): pass
class PermissionDeniedError(Exception): pass


# =========================
# USER FIRST LOGIN
# =========================
def create_user_first_login(
    db,
    firebase_uid: str,
    fcm_token: str | None,
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

        # 🔥 update FCM token if changed
        if fcm_token and user.fcm_token != fcm_token:
            user.fcm_token = fcm_token
            db.commit()
            print(f"[FCM] Updated token for user {user.id}")

        return {
            "id": user.id,
            "firebase_uid": firebase_uid,
            "email": user.email,
            "full_name": user.full_name,
        }

    # 2️⃣ Check if user exists by email
    user = user_repo.get_user_by_email(email)

    # 3️⃣ Create user if not exists
    if not user:
        user = user_repo.create_user(
            email=email,
            full_name=payload.get("full_name"),
            preferred_language=payload.get("preferred_language", "en"),
            is_commuter=payload.get("is_commuter", False),
            is_business_owner=payload.get("is_business_owner", False),
            fcm_token=fcm_token
        )
        print(f"[USER] Created new user {user.id}")

    else:
        # 🔥 update FCM token if existing email user logs in
        if fcm_token and user.fcm_token != fcm_token:
            user.fcm_token = fcm_token
            db.commit()
            print(f"[FCM] Updated token for existing email user {user.id}")

    user_id = user.id

    # 4️⃣ Create auth identity (avoid duplicates if possible)
    try:
        auth_repo.create_auth_identity(
            firebase_uid=firebase_uid,
            entity_id=user_id,
            entity_type=entity_type
        )
    except IntegrityError:
        print("[AUTH] Identity already exists, skipping")

    db.commit()

    return {
        "id": user_id,
        "firebase_uid": firebase_uid,
        "email": user.email,
        "full_name": user.full_name,
    }


# =========================
# ADMIN FIRST LOGIN
# =========================
def create_admin_first_login(
    db,
    creator_firebase_uid: str,
    new_user,
    create_firebase_user,
    fcm_token: str | None = None
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

    # Firebase user creation
    firebase = create_firebase_user(
        email=new_user.email,
        password="DefaultPassword123!",
        display_name=new_user.full_name,
    )

    # Local user creation
    user = user_repo.create_user(
        email=new_user.email,
        full_name=new_user.full_name,
        preferred_language="en",
        fcm_token=fcm_token
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


# =========================
# GET CURRENT USER
# =========================
def get_current_user(db, firebase_uid: str):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        return None

    return user_repo.get_user_by_id(user_id)


# =========================
# UPDATE CURRENT USER
# =========================
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