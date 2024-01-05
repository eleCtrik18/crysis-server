from src.models.payment import (
    Mandate,
    UserBank,
    MandateNotification,
    MandateTransaction,
)
from src.utils.datetimeutils import get_current_datetime_obj

# from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload


class MandateRepository:
    def __init__(self, db, user_id=None) -> None:
        self.db = db
        self.user_id = user_id

    def get_mandate_by_recur(self, recurrence="DAILY"):
        exists = (
            self.db.query(Mandate)
            .filter(
                Mandate.user_id == self.user_id,
                Mandate.recurrence == recurrence,
                Mandate.status == "ACTIVE",
            )
            .first()
        )
        return exists

    def initialize_mandate(self, data):
        exists = self.get_mandate_by_recur(recurrence=data["recurrence"])
        if exists:
            raise ValueError(f"Mandate of {data['recurrence']} already exists")
        obj = Mandate(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_mandate_by_refno(self, mandate_ref) -> Mandate:
        return self.db.query(Mandate).filter(Mandate.mandate_ref == mandate_ref).first()

    def update(self, updated_mandate_obj: Mandate):
        self.db.add(updated_mandate_obj)
        self.db.commit()
        self.db.refresh(updated_mandate_obj)
        return updated_mandate_obj

    def get_mandate_by_id(self, mandate_id):
        if self.user_id is not None:
            obj: Mandate = (
                self.db.query(Mandate)
                .filter(Mandate.user_id == self.user_id, Mandate.id == mandate_id)
                .first()
            )
        else:
            obj: Mandate = (
                self.db.query(Mandate).filter(Mandate.id == mandate_id).first()
            )
        return obj

    def get_active_mandates_by_user_id(self):
        objs: Mandate = (
            self.db.query(Mandate)
            .filter(Mandate.user_id == self.user_id, Mandate.status == "ACTIVE")
            .order_by(Mandate.created_at.desc())
        )
        return objs

    def get_all_active_mandates_daily(self):
        objs: Mandate = (
            self.db.query(Mandate)
            .filter(Mandate.status == "ACTIVE")
            .filter(Mandate.recurrence == "DAILY")
            .order_by(Mandate.created_at.desc())
        )
        return objs

    def get_all_active_unnotified_mandates_daily(self, from_date, to_date):
        objs = (
            self.db.query(Mandate)
            .filter(Mandate.status == "ACTIVE")
            .filter(Mandate.recurrence == "DAILY")
            .filter(
                or_(
                    and_(
                        Mandate.last_success_notify_date < to_date,
                        Mandate.last_success_notify_date > from_date,
                    ),
                    Mandate.last_success_notify_date == None,
                )
            )
            .order_by(Mandate.created_at.desc())
        )
        return objs

    def mark_mandate_revoked(self, mandate_id):
        man_obj = self.get_mandate_by_id(mandate_id)
        man_obj.status = "REVOKED"
        self.update(man_obj)

    def get_all_pending_mandates_daily(self):
        objs: Mandate = (
            self.db.query(Mandate)
            .filter(Mandate.status == "PENDING")
            .filter(Mandate.recurrence == "DAILY")
            .order_by(Mandate.created_at.desc())
        )
        return objs

    # def get_all_active_unnotified_mandates_daily(self, from_date, to_date):
    #     objs: Mandate = (
    #         self.db.query(Mandate)
    #         .filter(Mandate.status == "ACTIVE")
    #         .filter(Mandate.recurrence == "DAILY")
    #         # .filter(
    #         #     (func.date_trunc("day", Mandate.last_success_notify_date) < given_date)
    #         #     | (Mandate.last_success_notify_date == None)
    #         # )
    #         .filter(
    #             (
    #                 Mandate.last_success_notify_date
    #                 <= to_date & Mandate.last_success_notify_date
    #                 > from_date
    #             )
    #             | (Mandate.last_success_notify_date is None)
    #         )
    #         .order_by(Mandate.created_at.desc())
    #     )
    #     return objs


class MandateNotificationRepository:
    def __init__(self, db, user_id=None) -> None:
        self.db = db
        self.user_id = user_id

    def add_mandate_notification(self, mandate_id, data):
        mandate_obj: Mandate = MandateRepository(
            self.db, user_id=self.user_id
        ).get_mandate_by_id(mandate_id=mandate_id)
        if mandate_obj.last_success_notify_date:
            if (
                mandate_obj.last_success_notify_date.date
                == get_current_datetime_obj().date
            ):
                raise ValueError(f"Notification already sent to user. {self.user_id}")
        if mandate_obj and mandate_obj.status == "ACTIVE":
            mandate_obj.last_success_notify_date = get_current_datetime_obj()
            self.db.add(mandate_obj)

            data["status"] = "SENT"
            data["mandate_id"] = mandate_id
            obj = MandateNotification(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj

    def get_most_recent_notification(self, mandate_id):
        self.db.query(MandateNotification).filter(
            MandateNotification.mandate_id == mandate_id
        ).order_by(MandateNotification.expected_execution_date).last()

    def get_all_active_mandates_to_execute(self, threshold, user_id=None):
        objs: MandateNotification = (
            self.db.query(MandateNotification)
            .join(MandateNotification.mandate)
            .options(joinedload(MandateNotification.mandate))
            .filter(
                MandateNotification.status == "SENT",
                MandateNotification.created_at < threshold,
                Mandate.status == "ACTIVE",
            )
        )
        if user_id is not None:
            objs = objs.filter(Mandate.user_id == user_id)
        return objs

    def update_mandate_notification(self, notification_obj):
        self.db.add(notification_obj)
        self.db.commit()
        self.db.refresh(notification_obj)
        return notification_obj

    def get_notification_by_id(self, id) -> MandateNotification:
        return (
            self.db.query(MandateNotification)
            .filter(MandateNotification.id == id)
            .first()
        )


class MandateTransactionRepository:
    def __init__(self, db, user_id=None) -> None:
        self.db = db
        self.user_id = user_id

    def create_or_update(self, mandate_txn_obj):
        with self.db as session:
            session.add(mandate_txn_obj)
            session.commit()
            session.refresh(mandate_txn_obj)
        return mandate_txn_obj

    def get_mandate_txn_by_txn_no(self, txn_no, mandate_id):
        return (
            self.db.query(MandateTransaction)
            .filter(
                MandateTransaction.txn_no == txn_no,
                MandateTransaction.mandate_id == mandate_id,
            )
            .first()
        )

    def get_all_initiated_txns(self, txn_id=None):
        if txn_id:
            return self.db.query(MandateTransaction).filter(
                MandateTransaction.status == "INITIATED",
                MandateTransaction.id == txn_id,
            )
        return self.db.query(MandateTransaction).filter(
            MandateTransaction.status == "INITIATED",
        )

    def get_all_captured_txns(self):
        return self.db.query(MandateTransaction).filter(
            MandateTransaction.status == "CAPTURED",
        )

    def get_txn_by_id(self, txn_id):
        return (
            self.db.query(MandateTransaction)
            .filter(
                MandateTransaction.id == txn_id,
            )
            .first()
        )


class UserBankRepository:
    def __init__(self, db, user_id) -> None:
        self.db = db
        self.user_id = user_id

    def create(self, user_bank: UserBank):
        existing_user_bank = self.get_user_bank(user_bank.account_number)
        if not existing_user_bank:
            self.db.add(user_bank)
            self.db.commit()
            self.db.refresh(user_bank)
            return user_bank
        else:
            return existing_user_bank

    def get_user_bank(self, account_no: str) -> UserBank:
        return (
            self.db.query(UserBank)
            .filter(UserBank.account_number == account_no)
            .first()
        )
