from typing import List
from uuid import UUID

from pydantic import BaseModel

from src.notifications.NotificationSchemas import GetNotificationSettingsScheme


class GetSettingsScheme(BaseModel):
    user_uuid: str | UUID
    notifications: List[GetNotificationSettingsScheme] = []
