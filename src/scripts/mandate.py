from src.services.payment import UpiAutopayService
from src.repositories.payment import (
    MandateNotificationRepository,
    MandateRepository,
    MandateTransactionRepository,
)
from src.utils.datetimeutils import (
    get_current_datetime_obj,
    get_current_date_minus_x_minutes_obj,
)


def mandate_notification_sender(db, logger):
    from src.utils.logging_utils import send_slack_message

    one_day_mins_to_subtract = 24 * 60
    two_days_mins_to_subtract = (48 * 60) * 2  # change to two days

    to_date = get_current_date_minus_x_minutes_obj(one_day_mins_to_subtract)
    from_date = get_current_date_minus_x_minutes_obj(two_days_mins_to_subtract)
    logger.debug(f"TO-DATE: {to_date}", to_date)
    logger.debug(f"FROM-DATE: {from_date}", from_date)
    man_objs = MandateRepository(db=db).get_all_active_unnotified_mandates_daily(
        from_date, to_date
    )
    if man_objs.count() == 0:
        logger.info(
            f"No active mandates for the between {from_date} {to_date} to notify"
        )
        return
    logger.info("No of mandates to notify: {}".format(man_objs.count()))
    send_slack_message("No of mandates to notify: {}".format(man_objs.count()))
    for mandate_obj in man_objs:
        logger.info(f"Sending daily mandate notification for mandate {mandate_obj.id}")
        resp = UpiAutopayService(
            db=db, user_id=mandate_obj.user_id
        ).send_daily_mandate_notification(mandate_id=mandate_obj.id)
        logger.info(
            f"mandate notification response: {resp}, MandateID: {mandate_obj.id}"
        )


def update_pending_mandates(db, logger):
    from src.utils.logging_utils import send_slack_message

    db.expire_on_commit = False

    man_repo = MandateRepository(db=db)
    man_objs = man_repo.get_all_pending_mandates_daily()
    if man_objs.count() == 0:
        logger.info("No pending mandates to update")
        return
    logger.info("No of pending mandates to update: {}".format(man_objs.count()))
    # if man_objs.count() > 0:
    #     send_slack_message(
    #         "No of pending mandates to update: {}".format(man_objs.count())
    #     )

    for mandate_obj in man_objs:
        logger.info(f"Updating pending mandate {mandate_obj.id}")
        resp = UpiAutopayService(
            db=db, user_id=mandate_obj.user_id
        ).check_and_update_pending_status(mandate_id=mandate_obj.id)
        logger.info(
            f"mandate notification response: {resp}, MandateID: {mandate_obj.id}"
        )


def execute_mandates(db, logger, user_id=None):
    from src.utils.logging_utils import send_slack_message

    db.expire_on_commit = False
    notify_repo = MandateNotificationRepository(db=db)
    one_day_mins_to_subtract = (24 * 60) + 10  # keeping a buffer of 10 minutes

    current_date_minus_24hrs = get_current_date_minus_x_minutes_obj(
        one_day_mins_to_subtract
    )
    if str(user_id) == "-1":
        user_id = None
    objs = notify_repo.get_all_active_mandates_to_execute(
        current_date_minus_24hrs, user_id
    )
    logger.info(
        f"Got mandates to execute for date before {current_date_minus_24hrs} :{objs.count()}"
    )
    if objs.count() > 0:
        send_slack_message(
            f"Got mandates to execute for date before {current_date_minus_24hrs} :{objs.count()}"
        )
    for notification in objs:
        logger.info(f"Executing mandate {notification.mandate_id}")
        logger.info(f"Executing mandate notification {notification.id}")

        resp = UpiAutopayService(
            db=db, user_id=notification.mandate.user_id
        ).execute_mandate(notif_obj=notification)
        logger.info(
            f"mandate notification response: {resp}, MandateID: {notification.mandate_id}"
        )
    return True


def update_mandate_transaction_status(db, logger, txn_id=-1):
    from src.utils.logging_utils import send_slack_message

    db.expire_on_commit = False
    man_txn_repo = MandateTransactionRepository(db=db)
    resp_dict = {}
    if str(txn_id) == "-1":
        txn_id = None
    txns = man_txn_repo.get_all_initiated_txns(txn_id=txn_id)
    logger.info(f"Got Initiated Mandate transactions: {txns.count()}")
    if txns.count() > 0:
        send_slack_message(
            f"Updating Initiated Mandate transactions: count: {txns.count()}"
        )
    for txn in txns:
        resp = UpiAutopayService(db=db).check_and_update_mandate_transaction(txn)
        if resp:
            resp_dict[txn.id] = resp.data.get("status")
    if txns.count() > 0:
        send_slack_message(
            f"updated Initiated Mandate transactions: {txns.count()}, updated transactions: {resp_dict}"
        )

    return True


def check_and_credit_gold(db, logger):
    from src.utils.logging_utils import send_slack_message

    txn_repo = MandateTransactionRepository(db)
    db.expire_on_commit = False

    cap_txns = txn_repo.get_all_captured_txns()
    if cap_txns.count() > 0:
        pass
        send_slack_message(f"Crediting gold to txns: {cap_txns.count()}")
    else:
        return
    for txn in cap_txns:
        resp = UpiAutopayService(db=db).credit_gold_to_captured_txns(txn_obj=txn)

        logger.info(f"Credit gold resp: {resp}")
