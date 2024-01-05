from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import Column, Integer, DateTime, Text
from src.db.utils import utcnow, get_table_name
from sqlalchemy.sql import func


@declarative_mixin
class AuditMixin:
    """
    utcnow vs func.now
    https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime/33532154#33532154
    """

    created_by_user_id = Column(Integer, nullable=False)
    updated_by_user_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.timezone("Asia/Kolkata", func.now()),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.timezone("Asia/Kolkata", func.now()),
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return get_table_name(cls.__name__)
