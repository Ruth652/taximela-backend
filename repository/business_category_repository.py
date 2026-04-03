from domain.business_category_model import BusinessCategory

class BusinessCategoryRepository:

    def __init__(self, db):
        self.db = db

    def get_all_categories(self):
        categories = self.db.query(BusinessCategory).all()

        return [
            {
                "id": c.id,
                "name": c.name
            }
            for c in categories
        ]
    def get_by_id(self, category_id):
        return (
            self.db.query(BusinessCategory)
            .filter(BusinessCategory.id == category_id)
            .filter()
        )