from src.db.base_class import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from src.models.users import User
from sqlalchemy.orm import relationship


class Wallet(Base):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="wallets")
    qty_g = Column(Float, nullable=False,default=0)
    product_name = Column(
        String, nullable=False, default="GOLD24"
    )  # GOLD24, GOLD22, SILVER, should be indexed later
