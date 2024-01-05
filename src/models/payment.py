from src.db.base_class import Base
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    BigInteger,
)
from src.models.users import User
from sqlalchemy.orm import validates, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type


class UserBank(Base):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="banks")
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False, default="00000000000")
    ifsc_code = Column(String, nullable=False)
    account_type = Column(String, nullable=False, default="SAVINGS")
    account_holder_name = Column(String, nullable=False)
    vpa = Column(String, nullable=False)

    mandates = relationship("Mandate", back_populates="bank")


class Mandate(Base):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="mandates")
    amount = Column(Float, nullable=False)
    recurrence = Column(String)  # DAILY, MONTHLY, WEEKLY
    recur_day = Column(String, nullable=True)  # incase of week
    recur_date = Column(Integer, nullable=True)  # incase of month
    attached_vpa_id = Column(String, nullable=True)
    mandate_ref = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    status = Column(
        String, nullable=False, default="DEEPLINK_GENERATED"
    )  # REVOKED, ACTIVE, FAILED, PENDING, REJECTED, PAUSE, UNPAUSE
    pattern = Column(String, nullable=False, default="ASPRESENTED")
    bank_id = Column(Integer, ForeignKey(UserBank.id), nullable=True)
    bank = relationship("UserBank", back_populates="mandates")
    txn_no = Column(String, nullable=False, default="test")
    meta_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    last_success_notify_date = Column(DateTime(timezone=True), nullable=True)
    last_success_execution_date = Column(DateTime(timezone=True), nullable=True)
    notifications = relationship("MandateNotification", back_populates="mandate")
    transactions = relationship("MandateTransaction", back_populates="mandate")

    @validates("recurrence")
    def validate_recurrence(self, key, recurrence):
        assert recurrence in ["DAILY", "MONTHLY", "WEEKLY"]
        return recurrence

    @validates("recur_day")
    def validate_recur_day(self, key, recur_day):
        if recur_day:
            assert recur_day in ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        return recur_day


class MandateNotification(Base):
    mandate_id = Column(Integer, ForeignKey(Mandate.id), nullable=False)
    mandate = relationship("Mandate", back_populates="notifications")
    status = Column(
        String, nullable=False, default="SENT"
    )  # SENT, EXECUTED, EXECUTION_PENDING, EXECUTION_FAILED
    meta_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    seq_no = Column(String, nullable=False, default="")
    expected_execution_date = Column(DateTime(timezone=True), nullable=True)
    mandate_transaction = relationship(
        "MandateTransaction", back_populates="notification"
    )

    __table_args__ = (UniqueConstraint("mandate_id", "seq_no"),)


class MandateTransaction(Base):
    notification = relationship(
        "MandateNotification", back_populates="mandate_transaction"
    )
    notification_id = Column(
        BigInteger, ForeignKey(MandateNotification.id), nullable=False
    )
    mandate_id = Column(Integer, ForeignKey(Mandate.id), nullable=False)
    mandate = relationship("Mandate", back_populates="transactions")
    status = Column(
        String, nullable=False, default="INITIATED"
    )  # INITIATED, CAPTURED, FAILED, SUCCESS
    meta_data = Column(mutable_json_type(dbtype=JSONB, nested=True))

    execution_ref = Column(String, nullable=True)
    txn_no = Column(String, nullable=False)
    bank_rrn = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("txn_no"),)

    """
    get mandate notification:
    mandate_transaction_id == null
    status == "SENT"
    current_date - updated_at > 24 hours
    """
