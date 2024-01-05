from src.db.base_class import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from src.models.users import User
from sqlalchemy.orm import relationship


class Invoice(Base):
    download_url = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="invoices")
    last_downloaded = Column(DateTime(timezone=True), nullable=True)
