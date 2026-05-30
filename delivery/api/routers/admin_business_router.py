from fastapi import APIRouter, Depends, Path, Query,  HTTPException
from datetime import datetime

from sqlalchemy.orm import Session
from domain.business_model import Business
from infrastructure.db_dependency import get_db
from delivery.api.controllers.admin_business_controller import (
    get_business_registrations_controller,
    get_business_registration_controller,
    review_business_application_controller,
    get_businesses_controller
)
from delivery.api.controllers.business_controller import get_business_controller, get_business_stats_controller
from delivery.api.dependencies.admin_auth import get_current_operational_admin
from domain.business_registration.schemas import BusinessRegistrationFilterDTO
from domain.business.schemas import BusinessFilterDTO
from domain.business_registration.schemas import ReviewBusinessApplicationRequest
from domain.admin_model import Admin
from delivery.api.controllers.admin_business_controller import review_business_application_controller
from repository.auth_identity_repository import AuthIdentityRepository
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from uuid import UUID




router = APIRouter(
    prefix="/api/admin",
    tags=["Admin - Business-management"]
)


@router.get("/business-registrations")
async def get_business_registrations(
    filters: BusinessRegistrationFilterDTO = Depends(),
    admin=Depends(get_current_operational_admin),
    db: Session = Depends(get_db),
):

    filters.validate_dates()

    return await get_business_registrations_controller(
        db=db,
        status=filters.status,
        user_id=filters.user_id,
        from_date=filters.from_date,
        to_date=filters.to_date,
        search=filters.search,
        page=filters.page,
        limit=filters.limit
    )

@router.get("/business-registrations/{registration_id}")
async def get_business_registrations(
    registration_id: str, 
    admin=Depends(get_current_operational_admin),
    db: Session = Depends(get_db),
):
    return await get_business_registration_controller(registration_id,db)

@router.patch("/business-registrations/{registration_id}")
async def review_business_application(
    registration_id: str,
    body: ReviewBusinessApplicationRequest,
    admin: Admin = Depends(get_current_operational_admin),
    db: Session = Depends(get_db),
):
    return review_business_application_controller(
        db=db,
        registration_id=registration_id,
        action=body.action,
        admin_id=admin.id,
        rejection_reason=body.rejection_reason,  
    )

@router.get("/business/stats")
async def get_business_stats(
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    return get_business_stats_controller(
        db,
        user_id=user['uid']
    )

@router.get("/businesses")
async def get_businesses(
    filters: BusinessFilterDTO = Depends(),
    admin=Depends(get_current_operational_admin),
    db: Session = Depends(get_db),
):

    filters.validate_dates()

    return await get_businesses_controller(
        db=db,
        status=filters.status,
        user_id=filters.user_id,
        from_date=filters.from_date,
        to_date=filters.to_date,
        search=filters.search,
        page=filters.page,
        limit=filters.limit
    )

    
@router.get("/business/{business_id}")
async def get_business_details(
    business_id: UUID,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    print(business_id)
    
    return get_business_controller(
        db,
        user_id=user['uid'],
        business_id=business_id
    )

    
