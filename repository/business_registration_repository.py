from domain.business_model import Business
from domain.business_registration_model import BusinessRegistration
from domain.business_category_model import BusinessCategory
from domain.user_model import User
from datetime import datetime
from domain.admin_model import Admin
from sqlalchemy.orm import joinedload



class  BusinessRegistrationRepository:

    def __init__(self, db):
        self.db = db

    def get_filtered_registrations(
        self,
        status,
        user_id,
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
        if user_id:
            query = query.filter(
                BusinessRegistration.user_id == user_id
            )

        if status:
            query = query.filter(BusinessRegistration.status == status)

        if from_date:
            query = query.filter(BusinessRegistration.created_at >= from_date)

        if to_date:
            query = query.filter(BusinessRegistration.created_at <= to_date)

        if search:
            query = query.filter(BusinessCategory.name == search.upper())

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
                    "owner_profile_picture_url": r.user.profile_picture_url,
                    "submitted_at": r.created_at,
                    "status": r.status,
                }
                for r in records
            ],
            "total": total,
            "page": page,
            "limit": limit,
        }

    def get_registration_by_id(self, registration_id):

        registration = (
            self.db.query(BusinessRegistration)
            .filter(BusinessRegistration.id == registration_id)
            .first()
        )

        if not registration:
            return None

        owner = (
            self.db.query(User)
            .filter(User.id == registration.user_id)
            .first()
        )

        category = (
            self.db.query(BusinessCategory)
            .filter(BusinessCategory.id == registration.category_id)
            .first()
        )

        # reviewer = None
        # if registration.reviewed_by:
        #     reviewer = (
        #         self.db.query(Admin)
        #         .join(User, User.id == Admin.user_id)
        #         .filter(Admin.id == registration.reviewed_by)
        #         .first()
        #     )
        reviewer = None
        if registration.reviewed_by:
            reviewer = (
                self.db.query(Admin)
                .options(joinedload(Admin.user))
                .filter(Admin.id == registration.reviewed_by)
                .first()
            )

        return {
            "id": registration.id,
            "business_name": registration.business_name,

            "category": {
                "id": category.id if category else None,
                "name": category.name if category else None
            },

            "owner": {
                "id": owner.id,
                "full_name": owner.full_name,
                "email": owner.email,
                "owner_profile_picture_url": owner.profile_picture_url,
            },

            "location": {
                "latitude": registration.latitude,
                "longitude": registration.longitude
            },

            "documents": {
                "government_id_fan": registration.government_id_fan,
                "government_id_photo_url": registration.government_id_photo_url,
                "business_license_photo_url": registration.business_license_photo_url
            },

            "status": registration.status,
            "rejection_reason": registration.rejection_reason,

            "reviewed_by": {
                "id": reviewer.id,
                "full_name": reviewer.user.full_name if reviewer.user else None
            } if reviewer else None,

            "reviewed_at": registration.reviewed_at,
            "submitted_at": registration.created_at
        }


    def get_by_id(self, registration_id):

        return (
            self.db.query(BusinessRegistration)
            .filter(BusinessRegistration.id == registration_id)
            .first()
        )

    def update_status(
        self,
        registration,
        status,
        admin_id,
        rejection_reason=None
    ):

        registration.status = status
        registration.reviewed_by = admin_id
        registration.reviewed_at = datetime.utcnow()
        registration.rejection_reason = rejection_reason

        self.db.commit()
        self.db.refresh(registration)

        print(f"Updated registration {registration.id} to status {status}")
        print(registration)
        return registration
    
    def get_business_stats(self):
        total_businesses = self.db.query(BusinessRegistration).count()
        approved_businesses = self.db.query(BusinessRegistration).filter(BusinessRegistration.status == 'approved').count()
        pending_businesses = self.db.query(BusinessRegistration).filter(BusinessRegistration.status == 'pending_review').count()
        rejected_businesses = self.db.query(BusinessRegistration).filter(BusinessRegistration.status == 'rejected').count()

        return {
            "total_businesses": total_businesses,
            "approved_businesses": approved_businesses,
            "pending_businesses": pending_businesses,
            "rejected_businesses": rejected_businesses
        }



