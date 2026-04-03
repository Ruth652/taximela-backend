from fastapi import HTTPException, status
from usecases.service_provider_usecase import (
    ServiceProviderPermissionsError, 
    create_business_registration_usecase,
    get_my_applications_usecase, 
    get_my_application_usecase, 
    get_business_categories_usecase, 
    get_my_businesses_usecase,
    get_business_by_id_usecase,
    update_business_usecase,
    get_dashboard_summary_usecase
    )
from delivery.api.dependencies.service_provider_auth import verify_service_provider_permission

async def create_business_registration_controller(db, user, payload):
    try:
        firebase_uid = user["uid"]
        # verify_service_provider_permissions(db, firebase_uid)
        result = create_business_registration_usecase(
            db,
            firebase_uid,
            payload
        )

        return {
            "message": "Business registration submitted successfully",
            "data": result
        }
    except ServiceProviderPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        print("🔥 ERROR:", str(e))  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)   
        )

async def get_my_applications_controller(db, user, status, page, limit):
    try:
        firebase_uid = user["uid"]

        result = get_my_applications_usecase(
            db,
            firebase_uid,
            status,
            page,
            limit
        )

        return {
            "data": result["data"],
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"]
        }

    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )

async def get_my_application_controller(db, user, registration_id):
    try:
        firebase_uid = user["uid"]

        result = get_my_application_usecase(
            db,
            firebase_uid,
            registration_id
        )

        return result

    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )
async def get_business_categories_controller(db):
    try:
        result = get_business_categories_usecase(db)

        return result

    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )

async def get_my_businesses_controller(db, user, status, page, limit):
    try:
        firebase_uid = user["uid"]

        result = get_my_businesses_usecase(
            db,
            firebase_uid,
            status,
            page,
            limit
        )

        return {
            "data": result["data"],
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"]
        }

    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(status_code=500, detail="Something went wrong")
async def get_business_by_id_controller(db, user, business_id):
    try:
        firebase_uid = user["uid"]

        result = get_business_by_id_usecase(
            db,
            firebase_uid,
            business_id
        )

        return {"data": result}

    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

async def update_business_controller(db, user, business_id, payload):
    try:
        firebase_uid = user["uid"]
        result = update_business_usecase(db, firebase_uid, business_id, payload)
        return {"data": result, "message": "Business updated successfully"}
    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))  

async def get_dashboard_summary_controller(
    db,
    user
):
    """
    Fetch the dashboard summary for a service provider.
    Returns total applications, pending, approved, and rejected counts.
    """
    try:
        firebase_uid = user["uid"]
        summary = get_dashboard_summary_usecase(db, firebase_uid)
        return summary
    except ServiceProviderPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )