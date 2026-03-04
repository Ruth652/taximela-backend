from domain.business_registration_model import BusinessRegistration
from domain.business_category_model import BusinessCategory
from domain.user_model import User


class  BusinessRegistrationRepository:

    def __init__(self, db):
        self.db = db

    def get_filtered_registrations(
        self,
        status,
        from_date,
        to_date,
        search,
        page,
        limit
    ):
        query = (
            self.db.query(BusinessRegistration)
            .join(User)
            .join(BusinessCategory)
        )

        if status:
            query = query.filter(BusinessRegistration.status == status)

        if from_date:
            query = query.filter(BusinessRegistration.created_at >= from_date)

        if to_date:
            query = query.filter(BusinessRegistration.created_at <= to_date)

        if search:
            query = query.filter(BusinessCategory.name == search)

        total = query.count()

        records = (
            query.order_by(BusinessRegistration.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "data": [
                {
                    "id": r.id,
                    "business_name": r.business_name,
                    "owner_name": r.user.full_name,
                    "profile_picture_url": r.user.profile_picture_url,
                    "submitted_at": r.created_at,
                    "status": r.status,
                }
                for r in records
            ],
            "total": total,
            "page": page,
            "limit": limit,
        }