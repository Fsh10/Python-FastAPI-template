from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import BOOLEAN, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression
from uuid_extensions import uuid7

from src.database import Base
from src.utils.base.BaseCrudModel import OrganizationIDMixin
from src.utils.base.UTCFieldsMixin import utc_datetime_field


class EventType(str, Enum):
    delete = "DELETE"
    create = "CREATE"
    update = "UPDATE"
    assigned = "ASSIGNED"


class EventName(str, Enum):
    sensor_box = "SENSOR_BOX"
    shift = "SHIFT"
    team = "TEAM"
    comment = "COMMENT"
    equipment = "EQUIPMENT"


class NotificationType(str, Enum):
    success = "success"
    warning = "warning"
    info = "info"


@utc_datetime_field("created_at")
class Notification(OrganizationIDMixin, Base):
    __tablename__ = "notification"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("user.uuid", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        nullable=False, default=NotificationType.info.value
    )
    event_name: Mapped[str] = mapped_column(nullable=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    subject = mapped_column(JSONB, nullable=True)
    object = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )
    is_read: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    created_by_user: Mapped[UUID] = mapped_column(
        ForeignKey("user.uuid"), nullable=False
    )


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True, server_default=text("uuid_generate_v4()")
    )
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("user.uuid", ondelete="CASCADE"), nullable=False
    )
    event_name: Mapped[str] = mapped_column(nullable=False)
    event_type: Mapped[str] = mapped_column(nullable=False)
    send: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    is_disabled: Mapped[bool] = mapped_column(
        BOOLEAN, default=False, server_default=expression.false()
    )
