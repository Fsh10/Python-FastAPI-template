from typing import Optional

from fastapi.routing import APIRoute

from src.organizations.OrganizationService import get_organization_service
from src.utils.base.BaseCrudRouter import BaseCrudRouter


class OrganizationRouter(BaseCrudRouter):
    def __init__(self):
        super().__init__(
            prefix="", service=get_organization_service(), tag="Organization"
        )

        self.rewrite_api_route(
            old_api_route_path=self.prefix,
            old_http_method="POST",
            new_route=APIRoute(
                path="",
                endpoint=self.service.create_entity,
                response_model=Optional[self.service.schemas.get_response_scheme],
                tags=[self.tag],
                methods=["POST"],
            ),
        )

        self.delete_api_route_if_exists(
            api_route_path=f"{self.prefix}" + "/{entity_id}", http_method="GET"
        )

        self.delete_api_route_if_exists(
            api_route_path=f"{self.prefix}" + "/{entity_id}", http_method="DELETE"
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="/{entity_id}",
                endpoint=self.service.delete_entity_by_id,
                tags=[self.tag],
                methods=["DELETE"],
            )
        )

        self.add_api_route_to_router(
            APIRoute(
                path="/{entity_id}",
                endpoint=self.service.get_entity_by_id,
                tags=[self.tag],
                response_model=Optional[self.service.schemas.get_response_scheme],
                methods=["GET"],
            )
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="{organization_id}/avatar",
                endpoint=self.service.upload_avatar,
                tags=[self.tag],
                methods=["POST"],
            )
        )

        self.add_api_route_to_router(
            api_route=APIRoute(
                path="{organization_id}/avatar",
                endpoint=self.service.delete_avatar,
                tags=[self.tag],
                methods=["DELETE"],
            )
        )

        self.add_api_route_to_router(
            APIRoute(
                path="/by_api_key/{api_key}",
                endpoint=self.service.get_all_by_api_key,
                tags=[self.tag],
                methods=["GET"],
                description="Get list of organization UUIDs by API key",
            )
        )


organization_router = OrganizationRouter()
