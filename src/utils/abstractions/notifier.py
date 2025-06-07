from abc import ABC, abstractmethod

from src.notifications.NotificationService import NotificationService


class Notifier(ABC):
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service

    @abstractmethod
    async def notify(self):
        raise NotImplementedError
