from fastapi import HTTPException
from repository.business_repository import BusinessRepository


class AdminUsecase:

    def __init__(self, db):
        self.db = db
        self.business_repo = BusinessRepository(db)

    def get_businesses(
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

        return self.business_repo.get_filtered_registrations(
            status=status,
            user_id = user_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            page=page,
            limit=limit
        )