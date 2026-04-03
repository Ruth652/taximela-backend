from sqlalchemy.orm import Session
from repository.user_repository import UserRepository
from usecases.service_provider_usecase import ServiceProviderPermissionsError


def verify_service_provider_permission(db: Session, firebase_uid: str):
    user_repo = UserRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)

    if not user:
        raise ServiceProviderPermissionsError("User not found")

    if not user.is_business_owner:
        raise ServiceProviderPermissionsError(
            "Only business owners can access this resource"
        )

    if user.status == "suspended":
        raise ServiceProviderPermissionsError("Account is suspended")

    return user