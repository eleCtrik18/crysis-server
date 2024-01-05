from src.repositories.users import UserRepository
from src.repositories.payment import (
    MandateRepository,
    UserBankRepository,
    MandateNotificationRepository,
    MandateTransactionRepository,
)
from src.models.payment import MandateNotification, MandateTransaction
from src.external.camspay import (
    send_mandate_notification,
    execute_mandate_at_camspay,
    setup_daily_mandate,
    check_transaction_status,
    check_mandate_status,
)
from src.external.moigold import credit_gold_to_user
from src.schema.common import APIResponse
from src.utils.datetimeutils import (
    get_next_recur_date_daily,
    get_current_datetime_obj,
    get_current_date_minus_x_minutes_obj,
)
from src.utils.mathutils import convert_amout_to_string
from src.models.payment import UserBank
from src.logging import logger


class UpiAutopayService:
    def __init__(self, db, user_id=None) -> None:
        self.user_id = user_id
        self.db = db

    def setup_upi_autopay_daily_mandate(self, amount):
        try:
            user_name = UserRepository(self.db).get_user_profile(self.user_id)[
                "display_name"
            ]
            resp = setup_daily_mandate(
                amount=amount, payer_name=user_name, user_id=self.user_id
            )
            mandate_data = {
                "user_id": self.user_id,
                "amount": str(amount),
                "recurrence": "DAILY",
                "mandate_ref": resp["mandate_ref"],
                "status": resp["status"],
                "start_date": resp["start_date"],
                "end_date": resp["end_date"],
                "meta_data": {"create_mandate_request": resp["meta_data"]},
                "txn_no": resp["txn_no"],
            }
            obj = MandateRepository(
                db=self.db, user_id=self.user_id
            ).initialize_mandate(mandate_data)
        except Exception as e:
            return APIResponse(data={}, success=False, error=str(e))

        return APIResponse(
            data={
                "link": resp["deeplink"],
                "mandate_id": obj.id,
                "mandate_ref": obj.mandate_ref,
            },
            success=True,
            error="",
        )

    def update_mandate_status(self, decrypted_resp):
        mandate_resp = decrypted_resp
        mandate_repo = MandateRepository(db=self.db, user_id=self.user_id)
        if mandate_resp["callback_type"] == "MANDATE_STATUS":
            mandate_obj = mandate_repo.get_mandate_by_refno(
                mandate_resp["cp_mandate_ref_no"]
            )

            if mandate_obj and mandate_obj.status in [
                "PENDING",
                "ACTIVE",
                "PAUSE",
                "UNPAUSE",
            ]:
                self.user_id = mandate_obj.user_id
                if mandate_obj.bank_id is None and mandate_resp.get("bankname"):
                    bank_id = self._get_or_create_bank(mandate_resp)
                    mandate_obj.bank_id = bank_id

                # update mandate

                meta_data = mandate_obj.meta_data
                if len(meta_data.keys()) > 0:
                    meta_data["mandate_callback"] = mandate_resp
                else:
                    meta_data = {"mandate_callback": mandate_resp}

                mandate_obj.meta_data = meta_data
                mandate_obj.status = mandate_resp["status"]
                mandate_repo.update(mandate_obj)
                return APIResponse(
                    data={"status": mandate_resp["status"]}, success=True, error=""
                )

        elif mandate_resp["callback_type"] == "MANDATE_EXECUTION":
            mn_txn_repo = MandateTransactionRepository(db=self.db, user_id=self.user_id)
            mandate_obj = mandate_repo.get_mandate_by_refno(
                mandate_resp["cp_mandate_ref_no"]
            )
            mandate_txn = mn_txn_repo.get_mandate_txn_by_txn_no(
                mandate_resp["trxn_no"], mandate_id=mandate_obj.id
            )
            if not mandate_txn:
                return APIResponse(success=False, error="mandate_txn not found")
            self.user_id = mandate_obj.user_id
            man_notification_repo = MandateNotificationRepository(
                db=self.db, user_id=self.user_id
            )
            if mandate_resp["status"] == "CAPTURED":
                if mandate_txn.status == "INITIATED":
                    mandate_txn.status = "CAPTURED"
                    mn_txn_repo.create_or_update(mandate_txn)
                    man_notification = man_notification_repo.get_notification_by_id(
                        mandate_txn.notification_id
                    )
                    man_notification.status = "EXECUTED"
                    man_notification_repo.update_mandate_notification(man_notification)

                    mandate_obj.last_success_execution_date = get_current_datetime_obj()
                    mandate_repo.update(mandate_obj)
                    return APIResponse(
                        data={"status": mandate_resp["status"]}, success=True, error=""
                    )

            elif mandate_resp["status"] == "FAILED":
                if mandate_resp.get("status_desc") == "DEBIT HAS BEEN FAILED - NA":
                    mandate_txn.status = "FAILED"
                    mn_txn_repo.create_or_update(mandate_txn)
                    man_notification = man_notification_repo.get_notification_by_id(
                        mandate_txn.notification_id
                    )
                    man_notification.status = "EXECUTION_FAILED"

                    man_notification_repo.update_mandate_notification(man_notification)
                    return APIResponse(
                        data={"status": mandate_resp["status"]}, success=True, error=""
                    )

    def _get_or_create_bank(self, mandate_resp):
        data = {
            "user_id": self.user_id,
            "bank_name": mandate_resp["bankname"],
            "account_number": mandate_resp["accountno"],
            "ifsc_code": mandate_resp["ifsc"],
            "account_holder_name": mandate_resp["accholdername"],
            "vpa": mandate_resp["payer_vpa"],
        }
        bank_obj = UserBank(**data)
        bank_id = (
            UserBankRepository(db=self.db, user_id=self.user_id).create(bank_obj).id
        )

        return bank_id

    def send_daily_mandate_notification(self, mandate_id):
        mandate_obj = MandateRepository(self.db, self.user_id).get_mandate_by_id(
            mandate_id=mandate_id
        )
        if not mandate_obj:
            return APIResponse(data={}, success=False, error="Could not find mandate.")
        mnr = MandateNotificationRepository(self.db, self.user_id)

        if (
            mandate_obj.last_success_notify_date
            and mandate_obj.last_success_notify_date.date()
            == get_current_datetime_obj().date()
        ):
            return APIResponse(
                data={},
                success=False,
                error="User already notified about the next execution date.",
            )

        resp = send_mandate_notification(
            mandate_ref_no=mandate_obj.mandate_ref,
            amount=convert_amout_to_string(amount=mandate_obj.amount),
            debit_date=get_next_recur_date_daily(),
            user_id=mandate_obj.user_id,
        )
        if resp.get("status") == "SENT":
            _data = {
                "mandate_id": mandate_id,
                "expected_execution_date": get_next_recur_date_daily(return_obj=True),
                "seq_no": resp.get("seq_no"),
                "status": resp.get("status"),
                "meta_data": resp.get("meta_data"),
            }
            notif_obj = mnr.add_mandate_notification(mandate_id, _data)

            return APIResponse(data={"notif_id": notif_obj}, success=True, error="")

        elif resp.get("status") == "REVOKED":
            mandate_obj.status = "REVOKED"
            MandateRepository(self.db, self.user_id).update(mandate_obj)
            return APIResponse(
                data={}, success=False, error="Mandate has been revoked."
            )
        elif resp.get("status") == "REJECTED":
            mandate_obj.status = "REJECTED"
            MandateRepository(self.db, self.user_id).update(mandate_obj)
            return APIResponse(
                data={}, success=False, error="Mandate has been revoked."
            )
        else:
            return APIResponse(
                data={}, success=False, error="Could not send mandate notification."
            )

    def execute_mandate(self, notif_obj: MandateNotification = None, notif_id=None):
        if notif_id:
            notif_obj = MandateNotificationRepository(
                db=self.db
            ).get_notification_by_id(notif_id)
        resp = execute_mandate_at_camspay(
            mandate_ref_no=notif_obj.mandate.mandate_ref,
            amount=convert_amout_to_string(notif_obj.mandate.amount),
            seq_no=notif_obj.seq_no,
            user_id=self.user_id,
        )

        txn_no = resp["txn_no"]
        mandate_ref = notif_obj.mandate.mandate_ref
        self.user_id = notif_obj.mandate.user_id
        mandate_id = notif_obj.mandate.id

        if resp["status"] == "INITIATED":
            mandate_txn_obj = MandateTransaction()
            mandate_txn_obj.mandate_id = notif_obj.mandate_id
            mandate_txn_obj.txn_no = txn_no
            mandate_txn_obj.status = "INITIATED"
            mandate_txn_obj.execution_ref = resp["execution_ref"]
            mandate_txn_obj.meta_data = resp["meta_data"]
            mandate_txn_obj.bank_rrn = resp["bank_rrn"]
            mandate_txn_obj.notification_id = notif_obj.id

            man_txn_obj = MandateTransactionRepository(
                db=self.db, user_id=self.user_id
            ).create_or_update(mandate_txn_obj)
            logger.info("Added transaction: {0}".format(man_txn_obj.id))
            return APIResponse(data={"status": resp["status"]}, success=True, error="")
        elif resp["status"] == "FAILED":
            logger.info(
                f"Unable to execute mandate {mandate_ref} due to {resp['status_desc']}"
            )
            txn_status = check_transaction_status(
                mandate_ref_no=mandate_ref, txn_no=txn_no, user_id=self.user_id
            )
            if txn_status["status_desc"] == "MANDATE HAS BEEN REVOKED - BD":
                MandateRepository(self.db, self.user_id).mark_mandate_revoked(
                    mandate_id=mandate_id
                )
            if txn_status["status_desc"] == "Execution Request Already Initiated":
                notif_obj.status = "EXECUTION_PENDING"
                MandateNotificationRepository(db=self.db).update_mandate_notification(
                    notif_obj
                )
            logger.info(
                f"User_ID {self.user_id} Transaction status: {txn_status['status']}"
            )
        elif resp["status"] == "TIMEDOUT":
            from src.utils.logging_utils import send_slack_message

            send_slack_message(f"Mandate execution timed out mandate_id: {mandate_id}")
            logger.error(f"Mandate execution timed out mandate_id: {mandate_id}")
        return APIResponse(data={"status": resp["status"]}, success=True, error="")

    def check_and_update_pending_status(self, mandate_id):
        man_repo = MandateRepository(self.db, self.user_id)
        mandate_obj = man_repo.get_mandate_by_id(mandate_id=mandate_id)
        if mandate_obj and mandate_obj.status == "PENDING":
            resp = check_mandate_status(
                mandate_ref_no=mandate_obj.mandate_ref,
                txn_no=mandate_obj.txn_no,
                user_id=mandate_obj.user_id,
            )

            if resp["status"] != "PENDING":
                mandate_obj.status = resp["status"]
                # todo: if a user already has a mandate in success state,
                # this mandate should be revoked
                man_repo.update(mandate_obj)
                return APIResponse(
                    data={"status": resp["status"]}, success=True, error=""
                )
            elif resp[
                "status"
            ] == "PENDING" and mandate_obj.created_at < get_current_date_minus_x_minutes_obj(
                x=10
            ):
                mandate_obj.status = "FAILED"
                man_repo.update(mandate_obj)
                return APIResponse(
                    data={"status": resp["status"]}, success=True, error=""
                )

    def check_and_update_mandate_transaction(self, txn_obj):
        logger.info(f"Trying to update transaction txn_id: {txn_obj.id}")
        man_repo = MandateRepository(self.db, self.user_id)
        mn_txn_repo = MandateTransactionRepository(db=self.db)
        man_notification_repo = MandateNotificationRepository(db=self.db)
        mandate_id = txn_obj.mandate_id
        mandate_obj = man_repo.get_mandate_by_id(mandate_id=mandate_id)
        if mandate_obj and mandate_obj.status == "ACTIVE":
            self.user_id = mandate_obj.user_id
            mandate_ref = mandate_obj.mandate_ref
            txn_no = txn_obj.txn_no
            txn_status = check_transaction_status(
                mandate_ref_no=mandate_ref, txn_no=txn_no, user_id=self.user_id
            )
            if txn_status["status"] == "CAPTURED" and txn_obj.status == "INITIATED":
                txn_obj.status = "CAPTURED"
                mn_txn_repo.create_or_update(txn_obj)
                man_notification = man_notification_repo.get_notification_by_id(
                    txn_obj.notification_id
                )
                man_notification.status = "EXECUTED"
                man_notification_repo.update_mandate_notification(man_notification)

                mandate_obj.last_success_execution_date = get_current_datetime_obj()
                man_repo.update(mandate_obj)
            else:
                logger.info(
                    f"trying to update NOT CAPTURED STATE txn_status {txn_status}"
                )
                if txn_status["status"] == "FAILED" and txn_obj.status == "INITIATED":
                    if txn_status.get("status_desc") in [
                        "DEBIT HAS BEEN FAILED - NA",
                        "DEBIT TIMEOUT - TD",
                        "COLLECT EXPIRED - BD",
                        "ADDRESS RESOLUTION IS FAILED - NA",
                        "Request Failed",
                        "CREDIT HAS BEEN FAILED - NA",
                        "BENEFICIARY BANK DEEMED HIGH RESPONSE TIME CHECK DECLINE - TD",
                        "REMITTER BANK DEEMED HIGH RESPONSE TIME CHECK DECLINE - TD",
                    ]:
                        txn_obj.status = "FAILED"
                        txn_obj.meta_data = txn_status
                        mn_txn_repo.create_or_update(txn_obj)
                        man_notification = man_notification_repo.get_notification_by_id(
                            txn_obj.notification_id
                        )
                        man_notification.status = "EXECUTION_FAILED"

                        man_notification_repo.update_mandate_notification(
                            man_notification
                        )
                    else:
                        logger.info(
                            f"trying to update unidentified txn_status {txn_status},"
                            f"txn_id: {txn_obj.id}"
                        )
                        txn_obj.meta_data = txn_status
                        mn_txn_repo.create_or_update(txn_obj)

            return APIResponse(
                data={"status": txn_status.get("status_desc", "PENDING")},
                success=True,
                error="",
            )

    def credit_gold_to_captured_txns(self, txn_obj):
        mandate_id = txn_obj.mandate_id
        try:
            mandate_obj = MandateRepository(db=self.db).get_mandate_by_id(
                mandate_id=mandate_id
            )
            self.user_id = mandate_obj.user_id
            amount = mandate_obj.amount
            user_phone = UserRepository(db=self.db).get_user_profile(
                user_id=self.user_id
            )["phone_number"]

            logger.info(
                f"TRYING credit gold to user {user_phone}, txn_id={txn_obj.id}, amount={amount}"
            )
            mn_txn_repo = MandateTransactionRepository(db=self.db)
            # # txn_obj = mn_txn_repo.get_txn_by_id(txn_id=txn_id)
            resp: APIResponse = credit_gold_to_user(
                amount=amount, code="AUTOPAY", phone=user_phone, txn_id=txn_obj.id
            )
            if resp.success:
                txn_obj.status = "SUCCESS"
                mn_txn_repo.create_or_update(txn_obj)

                return resp
            else:
                from src.utils.logging_utils import send_slack_message

                send_slack_message(
                    f"FAILED to credit gold to user {user_phone}, txn_id={txn_obj.id}"
                )
                return None
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            logger.error(f"CRTITIAL FAILED to credit gold to txn_id={txn_obj.id}:{tb}")
            from src.utils.logging_utils import send_slack_message

            send_slack_message(
                f"CRTITIAL FAILED to credit gold to txn_id={txn_obj.id}, error={str(e)}"
            )
            return
