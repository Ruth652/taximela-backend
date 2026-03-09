
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from domain.business_model import AdminUpdateBusinessRequest

from http.client import HTTPException
from usecases.admin_business_usecase import AdminUsecase
from usecases.admin_usecase import UserNotFoundError, AdminPermissionsError
from usecases.business_usecase import update_business_usecase

async def update_business_controller(
    db: Session,
    firebase_user: dict, 
    business_id: str, 
    payload: AdminUpdateBusinessRequest
    ):
    
    try:
        firebase_uid = firebase_user["uid"]
        business = update_business_usecase(db, firebase_uid, business_id, payload)
        return {"message": "Business Updated successfully",
                "business_id": business.id,
                "name": business.name,
                "status": business.status
                }
    except AdminPermissionsError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def get_business_controller(
    db,
    user_id,
    business_id,
    ):
    usecase = AdminUsecase(db)
    return usecase.get_business_details(business_id, user_id)
