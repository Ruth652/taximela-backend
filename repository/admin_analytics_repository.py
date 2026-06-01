from sqlalchemy import text


class AdminAnalyticsRepository:

    def __init__(self, db):
        self.db = db

    def get_total_users(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar()

    def get_total_businesses(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM businesses")
        ).scalar()

    def get_total_registrations(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM business_registrations")
        ).scalar()

    def get_total_contributions(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM contributions")
        ).scalar()