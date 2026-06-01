from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def start_scheduler(rebuild_function, expire_subscriptions_function=None):

    scheduler.add_job(
        rebuild_function,
        trigger="cron",
        hour=2,
        minute=0,
        id="nightly_rebuild",
        replace_existing=True
    )

    if expire_subscriptions_function:
        # Run every hour to catch expired subscriptions promptly
        scheduler.add_job(
            expire_subscriptions_function,
            trigger="interval",
            hours=1,
            id="expire_subscriptions",
            replace_existing=True
        )

    scheduler.start()
