from repository.admin_analytics_repository import AdminAnalyticsRepository


class AdminAnalyticsUsecase:

    def __init__(self, db):
        self.repo = AdminAnalyticsRepository(db)

    def get_total_analytics(self):
        return {
            "total_users": self.repo.get_total_users(),
            "total_businesses": self.repo.get_total_businesses(),
            "total_registrations": self.repo.get_total_registrations(),
            "contributions": self.repo.get_total_contributions(),
        }


    def get_contribution_trend(self, period):

        return self.repo.get_contribution_trend(
            period=period
        )

        
    def get_users_growth_analytics(self):
        return {"users_growth": self.repo.get_users_growth()}

    def get_businesses_growth_analytics(self):
        return {"businesses_growth": self.repo.get_businesses_growth()}

