from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from usecases.admin_business_usecase import (
    AdminUsecase
)
from usecases.admin_business_application_usecase import (
    AdminUsecase as AdminBusinessApplicationUsecase
)

async def get_business_registrations_controller(
    db,
    status,
    user_id,
    from_date,
    to_date,
    search,
    page,
    limit
):
    usecase = AdminUsecase(db)

    return usecase.get_business_registrations(
        status=status,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        limit=limit
    )

async def get_businesses_controller(
    db,
    status,
    user_id,
    from_date,
    to_date,
    search,
    page,
    limit
):
    usecase = AdminBusinessApplicationUsecase(db)

    return usecase.get_businesses(
        status=status,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        limit=limit
    )




async def get_business_registration_controller(
    registration_id,
    db
):

    usecase = AdminUsecase(db)
    return usecase.get_business_registration_by_id(registration_id)

def review_business_application_controller(
    db,
    registration_id,
    action,
    admin_id,
    rejection_reason=None
):
    print("inside controller")

    usecase = AdminUsecase(db)

    return usecase.review_business_application_usecase(
        registration_id=registration_id,
        action=action,
        rejection_reason=rejection_reason,
        admin_id=admin_id,
    )
  
