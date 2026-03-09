from fastapi import HTTPException
from domain.business_model import BusinessInformation
from domain.enums.business_registration_status import (
    BusinessRegistrationStatus,
    ApplicationAction
)
from repository.auth_identity_repository import AuthIdentityRepository
from repository.business_repository import BusinessRepository

from repository.business_registration_repository import (
    BusinessRegistrationRepository
)

class AdminUsecase:

    def __init__(self, db):
        self.db = db
        self.business_registration_repo = BusinessRegistrationRepository(db)

    def get_business_registrations(
        self,
        status=None,
        user_id=None,
        from_date=None,
        to_date=None,
        search=None,
        page=1,
        limit=20
    ):
        if search:
            search = search.upper()

        return self.business_registration_repo.get_filtered_registrations(
            status=status,
            user_id = user_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            page=page,
            limit=limit
        )

    def get_business_registration_by_id(self, registration_id):
        print("Inside usecase")

        registration = self.business_registration_repo.get_registration_by_id(registration_id)

        if not registration:
            raise ValueError("Business registration not found")

        return registration

    def review_business_application_usecase(
        self,
        registration_id: str,
        action: ApplicationAction,
        admin_id: str,
        rejection_reason: str | None = None
    ):

        business_repo = BusinessRepository(self.db)

        registration = self.business_registration_repo.get_by_id(registration_id)

        if not registration:
            raise HTTPException(404, "Business registration not found")

        if registration.status != BusinessRegistrationStatus.pending_review:
            raise HTTPException(400, "Application already reviewed")

        # APPROVE
        if action == ApplicationAction.approve:
            print("approve-usecase")

            business_repo.create_business_from_registration(
                registration,
                admin_id
            )

            self.business_registration_repo.update_status(
                registration=registration,
                status=BusinessRegistrationStatus.approved,
                admin_id=admin_id
            )

        # REJECT
        elif action == ApplicationAction.reject:

            self.business_registration_repo.update_status(
                registration=registration,
                status=BusinessRegistrationStatus.rejected,
                admin_id=admin_id,
                rejection_reason=rejection_reason
            )

        return {"message": "Application reviewed successfully"}
    
    def get_business_details(self, business_id, user_id):
        
        auth_repo = AuthIdentityRepository(self.db)
        admin_uuid = auth_repo.get_super_business_admin_uuid_by_firebase_uid([user_id])
        
        if not admin_uuid:
            raise HTTPException(403, "Unauthorized")
        
        business_repo = BusinessRepository(self.db)
        business = business_repo.get_business_by_id(business_id)

        if not business:
            raise HTTPException(404, "Business not found")

        return BusinessInformation(
            id=business.id,
            name=business.name,
            latitude=business.latitude,
            longitude=business.longitude,
            government_id_fan=business.government_id_fan,
            government_id_photo_url=business.government_id_photo_url,
            business_logo=business.business_logo,
            license_photo_url=business.license_photo_url,
            status=business.status,
            approved_by=business.approved_by,
            approver_name = business.approver.user.full_name if business.approver and business.approver.user else None,          
            category_id=business.category_id,
            category_name=business.category.name if business.category else None,
            approved_at=business.approved_at.isoformat() if business.approved_at else None,
            created_at=business.created_at.isoformat() if business.created_at else None,
            updated_at=business.updated_at.isoformat() if business.updated_at else None
        )