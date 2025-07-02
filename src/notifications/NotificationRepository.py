from src.notifications.NotificationModel import Notification
from src.utils.base.BaseRepository import BaseRepository


class NotificationRepository(BaseRepository):
    model = Notification


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()
