from usecases.admin_analytics_usecase import AdminAnalyticsUsecase


async def get_admin_total_analytics_controller(db):
    usecase = AdminAnalyticsUsecase(db)
    return usecase.get_total_analytics()


async def get_contribution_trend_controller(
    db,
    period
):
    usecase = AdminAnalyticsUsecase(db)

    return usecase.get_contribution_trend(
        period=period
    )

async def get_admin_users_growth_analytics_controller(db):
    usecase = AdminAnalyticsUsecase(db)
    return usecase.get_users_growth_analytics()

async def get_admin_businesses_growth_analytics_controller(db):
    usecase = AdminAnalyticsUsecase(db)
    return usecase.get_businesses_growth_analytics()

