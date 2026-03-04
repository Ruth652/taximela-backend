from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from usecases.admin_business_usecase import (
    AdminUsecase
)

async def get_business_registrations_controller(
    db,
    status,
    from_date,
    to_date,
    search,
    page,
    limit
):
    usecase = AdminUsecase(db)

    return usecase.get_business_registrations(
        status=status,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        limit=limit
    )