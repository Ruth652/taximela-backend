

from repository.auth_identity_repository import AuthIdentityRepository
from repository.business_repository import BusinessRepository
from usecases.admin_usecase import AdminPermissionsError
from usecases.user_usecase import UserNotFoundError


def update_business_usecase(db, firebase_uid, business_id, payload):
    auth_repo = AuthIdentityRepository(db)
    
    is_super_and_business_admin = auth_repo.get_super_business_admin_uuid_by_firebase_uid([firebase_uid])
    
    if not is_super_and_business_admin:
        raise AdminPermissionsError("Super Admin or Business Adminaccess required to update business details.")
    
    business_repo = BusinessRepository(db)
    
    business = business_repo.update_business(business_id, payload)

    if not business:
        raise UserNotFoundError("Business not found.")
    
    return business 