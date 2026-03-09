from fastapi import HTTPException
from domain.enums.business_registration_status import (
    BusinessRegistrationStatus,
    ApplicationAction
)
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