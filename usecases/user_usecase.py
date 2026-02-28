from sqlalchemy.exc import IntegrityError
from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository

class UserNotFoundError(Exception): pass
class NoUpdateFieldsError(Exception): pass

def create_user_first_login(db, firebase_uid: str, email: str, payload: dict | None = None, *,
                            entity_type: str = "user"):
    """
    Creates or links a user at first login.
    - default entity_type is "user" so you can reuse this for normal users.
    - to create/link an admin identity, call with entity_type="admin" from a privileged flow only.
    """

    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    # 0) Check auth_identity
    existing_user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if existing_user_id:
        user = user_repo.get_user_by_id(existing_user_id)
        return {
            "id": user.id,
            "firebase_uid": firebase_uid,
            "email": user.email,
            "full_name": user.full_name,
        }
    payload = payload or {}

    try:
        with db.begin():  
            # check the user table 
            user = user_repo.get_user_by_email(email)

            if not user:
                user = user_repo.create_user(
                    email=email,
                    full_name=payload.get("full_name"),
                    preferred_language=payload.get("preferred_language", "en"),
                    # set other server-side defaults here (status, created_by, etc.)
                )
                db.flush()  

            existing_user_id_after = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
            if existing_user_id_after:
                # another request linked it while we were creating the user;
                # prefer the existing link (avoid duplicate auth_identity)
                user = user_repo.get_user_by_id(existing_user_id_after)
            else:
                # create the bridge row that links firebase -> our user
                auth_repo.create_auth_identity(
                    firebase_uid=firebase_uid,
                    entity_id=user.id,
                    entity_type=entity_type
                )
            # Transaction commits here if no exception

    except IntegrityError:
        db.rollback()
        user = user_repo.get_user_by_email(email)
        if not user:
            raise
        existing_user_id_after = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
        if not existing_user_id_after:
            # best-effort: try to create link (may still fail if another raced)
            try:
                with db.begin():
                    auth_repo.create_auth_identity(
                        firebase_uid=firebase_uid,
                        entity_id=user.id,
                        entity_type=entity_type
                    )
            except Exception:
                raise

    user = user_repo.get_user_by_id(user.id)
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