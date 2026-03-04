from repository.business_registration_repository import (
    BusinessRegistrationRepository
)

class AdminUsecase:

    def __init__(self, db):
        self.db = db
        self.business_repo = BusinessRegistrationRepository(db)

    def get_business_registrations(
        self,
        status=None,
        from_date=None,
        to_date=None,
        search=None,
        page=1,
        limit=20
    ):

        if search:
            search = search.upper()

        return self.business_repo.get_filtered_registrations(
            status=status,
            from_date=from_date,
            to_date=to_date,
            search=search,
            page=page,
            limit=limit
        )