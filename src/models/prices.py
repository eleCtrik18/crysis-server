from src.db.base_class import Base
from sqlalchemy import Column, String, Float


class Gold24Price(Base):
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    source = Column(String, nullable=False)
    price_w_gst = Column(Float, nullable=False)
    price_wo_gst = Column(Float, nullable=False)
    applied_gst = Column(Float, nullable=False)
    aura_buy_price = Column(Float, nullable=True)
    aura_sell_price = Column(Float, nullable=True)
    src_price_w_gst = Column(Float, nullable=True)
    src_price_wo_gst = Column(Float, nullable=True)
