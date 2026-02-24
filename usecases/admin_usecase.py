from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository
from domain.admin_model import Admin


class AdminPermissionsError(Exception):
    pass
class UserNotFoundError(Exception):
    pass

def verify_admin_permissions(db, firebase_uid :str):

    auth_repo =AuthIdentityRepository(db)
    user_id =auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        raise UserNotFoundError("User not found for the provided Firebase UID.")
    
    admin =db.query(Admin).filter(
        Admin.user_id == user_id,
Admin.role.in_(["super_admin", "operational_admin"]),  

        Admin.is_active == True
    ).first()

    if not admin:
        raise AdminPermissionsError("Admin access required.")
    return admin


def list_users_for_admin(db, firebase_uid: str, page: int, limit: int , status: str =None):
    verify_admin_permissions(db, firebase_uid)

    user_repo= UserRepository(db)
    return user_repo.list_users(page,limit, status)

def update_user_status_usecase(db, firebase_uid: str, user_id: int, new_status: str):
    verify_admin_permissions(db, firebase_uid)

    user_repo = UserRepository(db)
    user= user_repo.update_user_status(user_id, new_status)

    if not user:
        raise UserNotFoundError("User not found.")
    return user 