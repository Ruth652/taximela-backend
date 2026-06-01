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
        
    def get_users_growth(self):
        result = self.db.execute(
            text("""
                SELECT
                    DATE_TRUNC('month', created_at) AS month,
                    COUNT(*) AS count
                FROM users
                GROUP BY month
                ORDER BY month
            """)
        )

        return [
            {
                "date": row.month.strftime("%Y-%m-%d"),
                "count": row.count
            }
            for row in result
        ]
        
    def get_businesses_growth(self):
        result = self.db.execute(
            text("""
                SELECT
                    DATE_TRUNC('month', created_at) AS month,
                    COUNT(*) AS count
                FROM businesses
                GROUP BY month
                ORDER BY month
            """)
        )

        return [
            {
                "date": row.month.strftime("%Y-%m-%d"),
                "count": row.count
            }
            for row in result
        ]