from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user

from domain.auth_identity_model import AuthIdentity
from domain.admin_model import Admin
from usecases.admin_usecase import AdminPermissionsError


def get_current_operational_admin(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
):
    firebase_uid = firebase_user["uid"]

    # Step 1: Find auth identity
    identity = (
        db.query(AuthIdentity)
        .filter(AuthIdentity.firebase_uid == firebase_uid)
        .first()
    )

    if not identity or identity.entity_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as admin",
        )

    # Step 2: Get admin record
    admin = (
        db.query(Admin)
        .filter(Admin.id == identity.entity_id)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin record not found",
        )

    # Role check (only business and super admin can access)
    if admin.role == "operational_admin":  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient admin privileges",
        )

    return admin

def verify_super_admin_permissions(db: Session, firebase_uid: str):
    from repository.admin_repository import AdminRepository

    admin_repo = AdminRepository(db)
    admin = admin_repo.get_admin_by_firebase_uid(firebase_uid)

    if not admin:
        raise AdminPermissionsError("Not an admin")

    # if admin.role != "super_admin":
    #     raise AdminPermissionsError("Only super admin can access this resource")

    if not admin.is_active:
        raise AdminPermissionsError("Admin account is inactive")

    return admin
