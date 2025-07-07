from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.NotificationSchemas import CreateNotificationScheme
from src.notifications.NotificationService import get_notification_service
from src.utils.abstractions.notifier import Notifier


class WebNotifier(Notifier):
    async def notify(
        self,
        session: AsyncSession,
        notification_params: CreateNotificationScheme,
    ):
        await self._notification_service.create_entity(
            create_notification_params=notification_params,
            session=session,
        )


web_notifier = WebNotifier(get_notification_service())
