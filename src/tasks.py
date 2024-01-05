from src.scripts.priceupdater import update_gold_price
from src.scripts.mandate import (
    mandate_notification_sender,
    update_pending_mandates,
    execute_mandates,
    update_mandate_transaction_status,
    check_and_credit_gold,
)
from src.db.session import get_task_db
from src.logging import logger
import requests
import json

from celery import shared_task


@shared_task(name="run_gold_updater")
def run_gold_updater():
    with get_task_db() as db_session:
        update_gold_price(db_session, logger)


@shared_task(name="run_mandate_notification_sender")
def run_mandate_notification_sender():
    with get_task_db() as db_session:
        mandate_notification_sender(db=db_session, logger=logger)


@shared_task(name="run_execute_mandates")
def run_execute_mandates():
    with get_task_db() as db_session:
        execute_mandates(db_session, logger)


@shared_task(name="run_update_pending_mandates")
def run_update_pending_mandates():
    with get_task_db() as db_session:
        update_pending_mandates(db_session, logger)


@shared_task(name="run_update_mandate_transaction_status")
def run_update_mandate_transaction_status():
    with get_task_db() as db_session:
        update_mandate_transaction_status(db_session, logger)


@shared_task(name="run_check_and_credit_gold")
def run_check_and_credit_gold():
    with get_task_db() as db_session:
        check_and_credit_gold(db_session, logger)


@shared_task(name="make_slack_request")
def make_slack_request(api_url, headers, payload):
    requests.post(api_url, headers=headers, data=json.dumps(payload))
