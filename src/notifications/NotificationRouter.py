from typing import List, Optional

from fastapi.routing import APIRoute

from src.notifications.NotificationService import get_notification_service
from src.utils.base.BaseCrudRouter import BaseCrudRouter


class NotificationRouter(BaseCrudRouter):
    def __init__(self):
        super().__init__(
            prefix="", service=get_notification_service(), tag="Notification"
        )

        self.delete_api_route_if_exists(api_route_path=self.prefix, http_method="POST")
        self.delete_api_route_if_exists(
            api_route_path=self.prefix + "/{entity_id}", http_method="PATCH"
        )
        self.delete_api_route_if_exists(
            api_route_path=self.prefix + "/{entity_id}", http_method="GET"
        )
        self.delete_api_route_if_exists(
            api_route_path=self.prefix + "/{entity_id}", http_method="DELETE"
        )

        self.rewrite_api_route(
            old_api_route_path=self.prefix,
            old_http_method="GET",
            new_route=APIRoute(
                path="",
                endpoint=self.service.get_all_entities,
                tags=[self.tag],
                response_model=Optional[List[self.service.schemas.get_response_scheme]],
                methods=["GET"],
            ),
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="/{notification_id}",
                endpoint=self.service.delete_entity_by_id,
                tags=[self.tag],
                methods=["DELETE"],
                description="Delete notification by notification_id",
            )
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="/mark_as_read/all",
                endpoint=self.service.mark_all_as_read,
                tags=[self.tag],
                methods=["PATCH"],
                description="Mark all notifications of current user as read",
            )
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="/mark_as_read/one/{notification_id}",
                endpoint=self.service.mark_as_read,
                tags=[self.tag],
                methods=["PATCH"],
                description="Mark notification by notification_id as read",
            )
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="/delete/all",
                endpoint=self.service.delete_all,
                tags=[self.tag],
                methods=["DELETE"],
                description="Delete all notifications of current user",
            )
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="/toggle",
                endpoint=self.service.toggle_notification,
                tags=[self.tag],
                methods=["PATCH"],
                description="Toggle send status for event_name of current user (False becomes True and vice versa)",
            )
        )


notification_router = NotificationRouter()
