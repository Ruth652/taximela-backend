from repository.admin_repository import AdminRepository
from repository.user_repository import UserRepository
from repository.auth_identity_repository import AuthIdentityRepository
from domain.admin_model import Admin, UpdateAdminRequest
from services.notification_service import NotificationService


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

def list_admins_for_super_admin(
    db,
    firebase_uid: str,
    page: int,
    limit: int,
    status: str = None,
    roles=None
):
    admin_repo = AdminRepository(db)
    return admin_repo.list_admins(page, limit, status, roles)

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

    # Notify admins if user was suspended
    try:
        if new_status == "suspended":
            NotificationService(db).notify(
                event="user_suspended",
                message=f"User {user_id} has been suspended",
            )
    except Exception:
        pass

    return user


def update_admin_usecase(db, firebase_uid: str, admin_id: str, payload: UpdateAdminRequest):
    auth_repo = AuthIdentityRepository(db)
    
    is_super = auth_repo.get_super_admin_uuid_by_firebase_uid([firebase_uid])
    
    if not is_super:
        raise AdminPermissionsError("Super Admin access required to update admin details.")
    

    user_repo = UserRepository(db)
    admin_repo = AdminRepository(db)
    
    admin = admin_repo.update_admin(admin_id, payload)

    if not admin:
        raise UserNotFoundError("Admin not found.")
    
    update_data = {}
    
    
    if getattr(payload, "full_name", None) is not None:
        update_data["full_name"] = payload.full_name
    if getattr(payload, "profile_picture_url", None) is not None:
        update_data["profile_picture_url"] = payload.profile_picture_url

    if update_data:
        updated_user = user_repo.update_user_profile(admin.user_id, update_data)
        if not updated_user:
            raise UserNotFoundError("Associated user not found.")

    return admin

def delete_admin_usecase(db, firebase_uid: str, admin_id: str):
    auth_repo = AuthIdentityRepository(db)
    
    is_super = auth_repo.get_super_admin_uuid_by_firebase_uid([firebase_uid])
    
    if not is_super:
        raise AdminPermissionsError("Super Admin access required to delete an admin.")
    
    admin_repo = AdminRepository(db)
    user_repo = UserRepository(db)
    
    admin = admin_repo.delete_admin(admin_id)
    user = user_repo.delete_user(admin.user_id)

    if not admin:
        raise UserNotFoundError("Admin not found.")

    # Notify super_admins that an admin was removed
    try:
        NotificationService(db).notify(
            event="admin_removed",
            message=f"Admin {admin_id} has been removed",
        )
    except Exception:
        pass

    return admin

