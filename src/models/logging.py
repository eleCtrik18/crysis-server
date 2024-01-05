from src.db.base import Base
from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type


class WebhookLog(Base):
    vendor = Column(String(), nullable=False)
    server_response_code = Column(Integer, nullable=True)
    request_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    headers = Column(String, nullable=True)
    error = Column(String(), nullable=True)


class VendorApiLog(Base):
    user_id = Column(BigInteger, nullable=True)
    vendor = Column(String(), nullable=False)
    encrypted_request_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    request_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    headers = Column(String, nullable=True)
    request_id = Column(Integer, nullable=True)
    response_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    encrypted_response_data = Column(mutable_json_type(dbtype=JSONB, nested=True))
    response_code = Column(Integer, nullable=True)
    url = Column(String, nullable=True)
