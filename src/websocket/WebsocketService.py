from fastapi import Depends

from src.utils.base.BaseService import BaseService

from .WebsocketRepository import (
    WebsocketRepository,
    get_websocket_repository,
)


class WebsocketService(BaseService):
    def __init__(self, repository: WebsocketRepository) -> None:
        super().__init__(repository)


def get_websocket_service(
    repository: WebsocketRepository = Depends(get_websocket_repository),
) -> WebsocketService:
    return WebsocketService(repository=repository)
