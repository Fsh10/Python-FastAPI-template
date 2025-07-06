from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.NotificationService import get_notification_service


class WebsocketRepository:
    @staticmethod
    async def get_user_notifications(user, session: AsyncSession):
        """Get user notifications."""
        try:
            notifications = await get_notification_service().get_all_filtered_entities(
                filters={"user_uuid": str(user.uuid), "is_read": False}, session=session
            )
            result = [notification.model_dump() for notification in notifications]
            return result
        except Exception as ex:
            return []


def get_websocket_repository() -> WebsocketRepository:
    return WebsocketRepository()
