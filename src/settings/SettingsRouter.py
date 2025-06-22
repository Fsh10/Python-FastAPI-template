from fastapi import APIRouter, Depends

from src.dependencies import CurrentUserDep, SessionDep
from src.notifications.NotificationService import (
    NotificationService,
    get_notification_service,
)
from src.settings.SettingsSchemas import GetSettingsScheme

settings_router = APIRouter(prefix="", tags=["Setting"])


@settings_router.get("")
async def get_user_settings(
    user: CurrentUserDep,
    session: SessionDep,
    notification_service: NotificationService = Depends(get_notification_service),
) -> GetSettingsScheme:
    notification_settings = await notification_service.get_user_notification_settings(
        user=user, session=session
    )
    return GetSettingsScheme(user_uuid=user.uuid, notifications=notification_settings)
