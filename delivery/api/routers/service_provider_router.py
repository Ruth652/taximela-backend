from fastapi import APIRouter, Depends, Path, Query
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from delivery.api.controllers.service_provider_controller import (
    create_business_registration_controller,
    get_my_applications_controller,
    get_my_application_controller,
    get_business_categories_controller,
    get_my_businesses_controller,
    get_business_by_id_controller,
    update_business_controller,
    get_dashboard_summary_controller
)
from domain.business_registration_model import BusinessRegistrationRequest, GetBusinessesRegistrationParams
from domain.business_model import GetBusinessesParams, UpdateBusinessRequest
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from uuid import UUID

router = APIRouter(
    prefix="/api",
    tags=["Service provider"] 
)

@router.post("/auth/business-registration")
async def register_business(
    payload: BusinessRegistrationRequest,
    db: Session = Depends(get_db),
    user:dict = Depends(verify_token)
):
    return await create_business_registration_controller(db, user, payload)


@router.get("/business-registrations")
async def get_my_applications(
    param: GetBusinessesRegistrationParams = Depends(),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    return await get_my_applications_controller(db, user, param.status, param.page, param.limit)

@router.get("/business-registrations/{id}")
async def get_my_application(
    id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    return await get_my_application_controller(db, user, id)


@router.get("/business-categories")
async def get_business_categories(
    db: Session = Depends(get_db),
    #user: dict = Depends(verify_token)   
):
    return await get_business_categories_controller(db)

@router.get("/businesses/dashboard-summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    return await get_dashboard_summary_controller(db, user)

@router.get("/businesses")
async def get_my_businesses(
    param: GetBusinessesParams = Depends(),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    return await get_my_businesses_controller(db, user, param.status, param.page, param.limit)


@router.get("/businesses/{business_id}")
async def get_business_by_id(
    business_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    return await get_business_by_id_controller(db, user, business_id)

@router.patch("/businesses/{business_id}")
async def update_business(
    business_id: str,
    payload: UpdateBusinessRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    return await update_business_controller(db, user, business_id, payload)
