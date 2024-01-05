from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from src.db.base_class import Base
from src.db.utils import utcnow
from sqlalchemy.dialects.postgresql import JSONB


class Partner(Base):
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    plan = Column(String, nullable=True)
    users = relationship("User", back_populates="partner")


class User(Base):
    partner_id = Column(Integer, ForeignKey(Partner.id), nullable=True)
    partner = relationship("Partner", back_populates="users")
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    country_code = Column(String, nullable=False, default="91")
    phone_number = Column(String, nullable=False, index=True, unique=True)
    display_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    email_verified = Column(Boolean, default=False, nullable=True)
    jwt_token = Column(String, nullable=True)
    last_login = Column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
    is_active = Column(Boolean, default=True)
    last_platform = Column(String, nullable=False, default="NP")  # android, ios, web
    current_app_version = Column(String, nullable=False, default="NP")
    dob = Column(String, nullable=True)  # DD-MM-YYYY
    kyc_verified = Column(Boolean, default=False, nullable=True)

    user_meta = relationship("UserMeta", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")
    kyc_details = relationship("UserKycDetail", back_populates="user")
    mandates = relationship("Mandate", back_populates="user")
    banks = relationship("UserBank", back_populates="user")

    @validates("phone_number")
    def validate_phone_number(self, key, phone_number):
        assert len(phone_number) == 10
        return phone_number

    @validates("email")
    def validate_email(self, key, email):
        if not email:
            return email
        assert "@" in email
        return email

    @validates("dob")
    def validate_dob(self, key, dob):
        if not dob:
            return dob
        assert len(dob) == 10
        assert dob[2] == "-"
        assert dob[5] == "-"
        assert dob[0:2] <= "31"
        assert dob[3:5] <= "12"
        assert dob[6:10] <= "2010"
        assert dob[6:10] >= "1920"
        return dob


class UserMeta(Base):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="user_meta")
    data_key = Column(String, nullable=False)
    data_value = Column(String, nullable=True)


class UserKycDetail(Base):
    kyc_verified_on = Column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
    kyc_verified_by = Column(String, nullable=False)
    kyc_data = Column(
        JSONB
    )  # https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    kyc_number = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    kyc_request_id = Column(String, nullable=True)
    user = relationship("User", back_populates="kyc_details")
