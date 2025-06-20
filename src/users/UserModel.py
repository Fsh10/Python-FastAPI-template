from datetime import datetime

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from src.database import Base, get_async_session
from src.utils.base.BaseCrudModel import BaseCrudModel, UUIDMixin
from src.utils.base.UTCFieldsMixin import utc_datetime_field


@utc_datetime_field("registered_at")
class User(SQLAlchemyBaseUserTable[int], BaseCrudModel, UUIDMixin, Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("avatar", "id", "email", name="unique_user_constraints"),
    )

    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    organization_id = Column(
        UUID, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False
    )
    avatar = Column(String, nullable=True)
    registered_at = Column(DateTime(timezone=True), default=datetime.now)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_working = Column(Boolean, default=False, nullable=False)
    send_report = Column(Boolean, default=False, nullable=True)
    time_zone = Column(String, nullable=False, default="Asia/Yekaterinburg")
    language = Column(String, nullable=False, default="ru")
    authorized_in_bot = Column(Boolean, server_default=expression.false())

    organization = relationship(
        "Organization", foreign_keys=[organization_id], lazy="select"
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
