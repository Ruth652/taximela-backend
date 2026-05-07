from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def start_scheduler(rebuild_function):

    scheduler.add_job(
        rebuild_function,
        trigger="cron",
        hour=2,
        minute=0,
        id="nightly_rebuild",
        replace_existing=True
    )

    scheduler.start()