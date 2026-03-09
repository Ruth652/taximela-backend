from fastapi import APIRouter, Depends, Path, Query,  HTTPException
from datetime import datetime

from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from delivery.api.controllers.admin_business_controller import (
    get_business_registrations_controller,
    get_business_registration_controller,
    review_business_application_controller,
    get_businesses_controller
)
from delivery.api.dependencies.admin_auth import get_current_operational_admin
from domain.business_registration.schemas import BusinessRegistrationFilterDTO
from domain.business.schemas import BusinessFilterDTO
from domain.business_registration.schemas import ReviewBusinessApplicationRequest
from domain.admin_model import Admin
from delivery.api.controllers.admin_business_controller import review_business_application_controller



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