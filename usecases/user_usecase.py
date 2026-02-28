from sqlalchemy.exc import IntegrityError
from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository

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
            user = user_repo.get_user_by_email(email)

            if not user:
                user = user_repo.create_user(
                    email=email,
                    full_name=payload.get("full_name"),
                    preferred_language=payload.get("preferred_language", "en"),
                )
                db.flush()

            existing_after = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
            if not existing_after:
                auth_repo.create_auth_identity(
                    firebase_uid=firebase_uid,
                    entity_id=user.id,
                    entity_type=entity_type
                )

    except IntegrityError:
        db.rollback()
        user = user_repo.get_user_by_email(email)
        if not user:
            raise
        existing_after = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
        if not existing_after:
            with db.begin():
                auth_repo.create_auth_identity(
                    firebase_uid=firebase_uid,
                    entity_id=user.id,
                    entity_type=entity_type
                )

    user = user_repo.get_user_by_id(user.id)

    return {
        "id": user.id,
        "firebase_uid": firebase_uid,
        "email": user.email,
        "full_name": user.full_name,
    }


def create_admin_by_creator(
    db,
    creator_firebase_uid: str,
    new_user_email: str,
    payload: dict | None = None,
    *,
    role: str | None = None,
    new_user_firebase_uid: str | None = None
):
    auth_repo = AuthIdentityRepository(db)
    user_repo = UserRepository(db)

    creator_user_id = auth_repo.get_user_uuid_by_firebase_uid(creator_firebase_uid)
    if not creator_user_id:
        raise UserNotFoundError()

    if not user_repo.is_admin(creator_user_id):
        raise PermissionDeniedError()

    payload = payload or {}

    try:
        with db.begin():
            user = user_repo.get_user_by_email(new_user_email)

            if not user:
                user = user_repo.create_user(
                    email=new_user_email,
                    full_name=payload.get("full_name"),
                    preferred_language=payload.get("preferred_language", "en"),
                )
                db.flush()

            if new_user_firebase_uid:
                existing_link = auth_repo.get_user_uuid_by_firebase_uid(new_user_firebase_uid)
                if not existing_link:
                    auth_repo.create_auth_identity(
                        firebase_uid=new_user_firebase_uid,
                        entity_id=user.id,
                        entity_type="admin" if role else "user"
                    )

            if role:
                user_repo.promote_to_admin(
                    user.id,
                    role=role,
                    created_by=creator_user_id
                )

    except IntegrityError:
        db.rollback()
        user = user_repo.get_user_by_email(new_user_email)
        if not user:
            raise

    user = user_repo.get_user_by_id(user.id)

    return {
        "id": user.id,
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