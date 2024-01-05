from apscheduler.schedulers.background import BackgroundScheduler

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.scripts.priceupdater import update_gold_price
from src.scripts.mandate import (
    mandate_notification_sender,
    update_pending_mandates,
    execute_mandates,
)
from src.db.session import SessionLocal
from src.logging import logger
from src.celery import celery_app

from datetime import time
import pytz

ist_timezone = pytz.timezone("Asia/Kolkata")

scheduler = BackgroundScheduler()


def run_mandate_notification_sender():
    db_session = SessionLocal()

    mandate_notification_sender(db=db_session, logger=logger)


@celery_app.task
def run_gold_updater():
    db_session = SessionLocal()

    update_gold_price(db_session, logger)


def run_update_pending_mandates():
    db_session = SessionLocal()

    update_pending_mandates(db_session, logger)


def run_execute_mandates():
    db_session = SessionLocal()

    execute_mandates(db=db_session, logger=logger)


scheduler.add_job(run_gold_updater, "interval", minutes=10)  # Run every 10 minutes

scheduler.add_job(
    run_mandate_notification_sender,
    "interval",
    minutes=10,
)  # Runs at 11 PM IST

scheduler.add_job(
    run_update_pending_mandates,
    "interval",
    minutes=15,
)  # Runs at 11 PM IST

# scheduler.add_job(
#     run_execute_mandates,
#     "interval",
#     # minutes=10,
#     seconds=5,
# )  # Runs at 11 PM IST


# Create a timezone object for IST

# # Create a time object for 11:00 PM IST
# run_mandate_notification_sender_time_1 = time(hour=23, minute=00, tzinfo=ist_timezone)
# run_mandate_notification_sender_time_2 = time(hour=11, minute=00, tzinfo=ist_timezone)


# scheduler.add_job(
#     run_mandate_notification_sender,
#     "cron",
#     hour=run_mandate_notification_sender_time_1.hour,
#     minute=run_mandate_notification_sender_time_1.minute,
#     second=0,
# )  # Runs at 11 PM IST

# scheduler.add_job(
#     run_mandate_notification_sender,
#     "cron",
#     hour=run_mandate_notification_sender_time_2.hour,
#     minute=run_mandate_notification_sender_time_2.minute,
#     second=0,
# )  # Runs at 11 PM IST
