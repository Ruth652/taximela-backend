from repository.business_registration_repository import BusinessRegistrationRepository
from repository.business_category_repository import BusinessCategoryRepository
from repository.business_repository import BusinessRepository
from repository.user_repository import UserRepository
from fastapi import HTTPException, status as http_status



class ServiceProviderPermissionsError(Exception):
    pass


def create_business_registration_usecase(db, firebase_uid: str, request):
    user_repo = UserRepository(db)
    business_repo = BusinessRegistrationRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # if not user.is_business_owner:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only business owners can access this endpoint"
    #     )
    try:
        duplicate = business_repo.is_duplicate(
            user.id,
            request.business_name,
            request.category_id
        )
    except Exception as e:
        print("🔥 DUPLICATE CHECK ERROR:", e)
        raise e

    if duplicate and duplicate.status == "pending_review":
        raise ServiceProviderPermissionsError("Application already pending")

    if duplicate and duplicate.status == "approved":
        raise ServiceProviderPermissionsError("Business already approved")
    if duplicate and duplicate.status == "rejected":
        pass
    registration = business_repo.create_registration({
            "user_id": user.id,
            "business_name": request.business_name,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "government_id_fan": request.government_id_fan,
            "government_id_photo_url": str(request.government_id_photo_url),
            "business_license_photo_url": str(request.business_license_photo_url),
            "category_id": request.category_id,
            "status": "pending_review"
        })

    if not user.is_business_owner:
        print(f"--- [TaxiMela] First registration detected. Promoting User {user.id} ---")
        user_repo.promote_to_business_owner(user)

    return registration

def get_my_applications_usecase(db, firebase_uid, status, page, limit):
    user_repo = UserRepository(db)
    business_repo = BusinessRegistrationRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_business_owner:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint"
        )
  
    return business_repo.get_my_registrations(
        user.id,
        status,
        page,
        limit
    )

def get_my_application_usecase(db, firebase_uid, registration_id):
    user_repo = UserRepository(db)
    business_repo = BusinessRegistrationRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)

    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # if not user.is_business_owner:
    #     raise HTTPException(
    #         status_code=http_status.HTTP_403_FORBIDDEN,
    #         detail="Only business owners can access this endpoint"
    #     )

    registration = business_repo.get_by_id(registration_id)

    if not registration:
        raise Exception("Application not found")

    
    if registration.user_id != user.id:
        raise Exception("Unauthorized access")

    return {
        "id": registration.id,
        "business_name": registration.business_name,
        "status": registration.status,
        "rejection_reason": registration.rejection_reason
    }
def get_business_categories_usecase(db):
    repo = BusinessCategoryRepository(db)
    return repo.get_all_categories()

def get_my_businesses_usecase(db, firebase_uid, status, page, limit):
    user_repo = UserRepository(db)
    business_repo = BusinessRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_business_owner:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint"
        )
    return business_repo.get_my_businesses(
        user.id,
        status,
        page,
        limit
    )

def get_business_by_id_usecase(db, firebase_uid, business_id):
    user_repo = UserRepository(db)
    business_repo = BusinessRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_business_owner:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint"
        )
    business = business_repo.get_business_by_id(business_id)
    if not business:
        raise Exception("Business not found")

    # Ensure user owns this business
    if business.owner_id != user.id:
        raise Exception("Unauthorized access to this business")

    return {
        "id": business.id,
        "business_name": business.name,
        "business_logo": business.business_logo,
        "status": business.status,
        "latitude": business.latitude,
        "longitude": business.longitude,
        "government_id_fan": business.government_id_fan,
        "government_id_photo_url": business.government_id_photo_url,
        "license_photo_url": business.license_photo_url,
        "category": {
            "id": business.category.id if business.category else None,
            "name": business.category.name if business.category else None
        },
        "approved_by": {
            "id": business.approved_by_admin.id if business.approved_by_admin else None,
            "full_name": business.approved_by_admin.user.full_name if business.approved_by_admin and business.approved_by_admin.user else None
        },
        "approved_at": business.approved_at,
        "created_at": business.created_at,
        "updated_at": business.updated_at
    }



def update_business_usecase(db, firebase_uid, business_id, payload):
    user_repo = UserRepository(db)
    business_repo = BusinessRepository(db)
    category_repo = BusinessCategoryRepository(db)  # for validation

    user = user_repo.get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_business_owner:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint"
        )
    business = business_repo.get_business_by_id(business_id)
    if not business:
        raise Exception("Business not found")

    if business.owner_id != user.id:
        raise Exception("Unauthorized to edit this business")

    updates = {}
    if getattr(payload, "business_name", None):
        updates["name"] = payload.business_name
    if getattr(payload, "latitude", None):
        updates["latitude"] = payload.latitude
    if getattr(payload, "longitude", None):
        updates["longitude"] = payload.longitude
    if getattr(payload, "business_logo", None):
        updates["business_logo"] = str(payload.business_logo)
    if getattr(payload, "category_id", None):
        # Check if category exists
        category = category_repo.get_by_id(payload.category_id)
        if not category:
            raise Exception("Category does not exist")
        updates["category_id"] = payload.category_id

    updated_business = business_repo.update_business(business, updates)

    return {
        "id": updated_business.id,
        "business_name": updated_business.name,
        "latitude": updated_business.latitude,
        "longitude": updated_business.longitude,
        "business_logo": updated_business.business_logo,
        "category_id": updated_business.category_id,
        "status": updated_business.status,
        "updated_at": updated_business.updated_at
    }

def get_dashboard_summary_usecase(db, firebase_uid: str):
    """
    Returns a summary of all business registrations for a user.
    """
    user_repo = UserRepository(db)
    business_repo = BusinessRegistrationRepository(db)

    user = user_repo.get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # if not user.is_business_owner:
    #     raise HTTPException(
    #         status_code=http_status.HTTP_403_FORBIDDEN,
    #         detail="Only business owners can access this endpoint"
    #     )
   
    stats = business_repo.get_user_business_stats(user.id)
    return stats
