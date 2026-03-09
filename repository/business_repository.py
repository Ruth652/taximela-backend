from domain.business_model import Business
#from datetime import datetime


class BusinessRepository:

    def __init__(self, db):
        self.db = db

    def create_business_from_registration(self, registration, admin_id):

        business = Business(
            owner_id=registration.user_id,
            name=registration.business_name,
            latitude=registration.latitude,
            longitude=registration.longitude,
            government_id_fan=registration.government_id_fan,
            government_id_photo_url=registration.government_id_photo_url,
            license_photo_url=registration.business_license_photo_url,
            category_id=registration.category_id,
            #approved_at= datetime.utcnow(),
            approved_by=admin_id
        )

        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)

        return business
    
    def get_business_by_id(self, business_id):
        return self.db.query(Business).filter(Business.id == business_id).first()
    