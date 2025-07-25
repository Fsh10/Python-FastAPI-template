import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.notifications.NotificationModel import NotificationType
from src.utils.base.BaseSchemasForRouter import BaseSchemasForRouter

"""
WARNING: THIS IS JUST TEST SCHEMAS, CHANGE IT IN REAL PROJECT
"""


class NotificationSchemas(BaseSchemasForRouter):
    def __init__(self):
        super().__init__(
            get_response_scheme=GetNotificationScheme,
            create_request_scheme=CreateNotificationScheme,
            update_request_scheme=None,
        )


class NotificationObject(BaseModel):
    id: str
    value: str


class GetNotificationSettingsScheme(BaseModel):
    id: str | UUID
    user_uuid: str | UUID
    event_name: str
    event_type: str
    send: bool
    is_disabled: bool


class CreateNotificationScheme(BaseModel):
    title: str = None
    user_uuid: str | UUID = None
    type: str = NotificationType.info.value
    event_name: str
    event_type: str
    subject: Optional[NotificationObject] = None
    object: Optional[NotificationObject] = None
    created_by_user: str | UUID
    organization_id: str | UUID


class GetNotificationScheme(CreateNotificationScheme):
    id: str | UUID
    user_uuid: str | UUID
    type: str
    event_name: str
    event_type: str
    title: str
    subject: Optional[NotificationObject] = None
    object: Optional[NotificationObject] = None
    created_at: datetime.datetime | str
    is_read: bool
    created_by_user: str | UUID
    organization_id: str | UUID

    @field_validator(
        "user_uuid",
        "id",
        "created_by_user",
        "organization_id",
        "created_at",
        mode="before",
    )
    def to_str(v):
        return str(v)


notification_schemas = NotificationSchemas()
