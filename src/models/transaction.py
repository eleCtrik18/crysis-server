from src.db.base_class import Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Float
from src.models.users import User
from sqlalchemy.orm import relationship
from src.models.invoice import Invoice
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type


class Transaction(Base):
    uuid = Column(String, nullable=False, index=True, unique=True)
    invoice_id = Column(
        Integer,
        ForeignKey(Invoice.id),
        nullable=True,
    )
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="transactions")
    qty_g = Column(Float, nullable=False)
    value_wo_gst_rs = Column(Float, nullable=False)
    gst_rs = Column(Float, default=0.0, nullable=False)
    total_value_rs = Column(Float, nullable=False)
    txn_status = Column(String, nullable=False, index=True)  # success, failed
    txn_type = Column(String, nullable=False, index=True)  # buy, sell
    txn_subtype = Column(String, nullable=False, index=True)  # COUPON, CASH, REFERRAL
    product_name = Column(
        String, nullable=False
    )  # GOLD24, GOLD22, SILVER, should be indexed later
    platform = Column(String, nullable=False)  # android, ios, web, api
    version = Column(String, nullable=True)  # app version Aura 1.0.0, Moi 1.0.0
    show_in_app = Column(Boolean, nullable=False, default=True)
    attached_coupon_code = Column(String, nullable=True)
    discount_rs = Column(Float, nullable=True, default=0.0)
    rate_per_g_wo_gst = Column(Float, nullable=False)
    payment_mode = Column(String, nullable=True)
    external_txn_id = Column(String, nullable=True)
    meta_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
