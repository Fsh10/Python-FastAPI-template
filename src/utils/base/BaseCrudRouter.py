from abc import ABC
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel

from src.dependencies import CurrentUserDep, SessionDep
from src.exceptions import NotFoundException
from src.utils.base.BaseService import BaseService, get_base_service


class BaseCrudRouter(APIRouter, ABC):
    """
    This class is made for split responsibilities. BaseCrudRouter - make basic things we need in REST-API
    automatically, and if you want some other functionality - override it and write your own logic. This class
    automatically add needed endpoints in this router. So if you want your own endpoint - override it and use
    rewrite_api_route function to replace existing route with yours This class is abstract, so you should implement
    this class:
    Class implementing should be like this:
    ```
    class EquipmentRouter(BaseCrudRouter):
        def __init__(self):
            super().__init__(prefix="/order",
                             model=Order,
                             repository=OrderRepository(),
                             schemas=order_schemas,
                             tags=["Order"])

    ```
    Always give tags - and if you don't - don't change tags field - because it is mutable
    """

    """
    :parameter model: this should be type of Model you use - it is made static for type hints
    """

    def __init__(
        self,
        prefix: str,
        service: Annotated[BaseService, Depends(get_base_service)],
        tag: str = "BaseCrud",
    ):
        """
        Excluding standard initialising params - it automatically add basic REST-API endpoints to itself
        :param prefix: path to this endpoint - for example prefix="/equipment" - path will be http://localhost:8000/equipment
        :param model: check model docs upper
        :param repository: this is repository for model you use - it is object, so create it when implementing class
        :param schemas: object of child class of BaseSchemasForRouter - check what fields it need - and I think you will get for what it needed
        :param tags: tags for OpenApi - it should be named as your model name - also - you shouldn't change it in class methods becaues it's mutable
        """
        self.tag = tag
        super().__init__(prefix=prefix, tags=[self.tag])
        self.service = service

        self.__add_base_routes_to_self()

    def delete_api_route_if_exists(self, api_route_path: str, http_method: str):
        route_from_router = self.first_or_none(
            filter(
                lambda route: route.path == api_route_path
                and http_method in route.methods,
                self.routes,
            )
        )
        if route_from_router is not None:
            self.routes.remove(route_from_router)

    def add_api_route_to_router(self, api_route: APIRoute) -> None:
        """
        Method to add api route in router with all it settings
        :param api_route: object of APIRoute classes
        :return: None
        """
        api_route.path = self.prefix + api_route.path
        self.routes.append(api_route)

    def rewrite_api_route(
        self, old_api_route_path: str, old_http_method: str, new_route: APIRoute
    ):
        """
        Also you can use it to add new api route
        :param old_http_method: http method of route we want delete (because there are can be different routes on one path)
        :param old_api_route_path: path of api route you want to replace - for example: "/equipment"
        :param new_route: new route object (of type APIRoute) - set all needed setting for you
        :return: None
        """
        self.delete_api_route_if_exists(
            api_route_path=old_api_route_path, http_method=old_http_method
        )
        self.add_api_route_to_router(new_route)

    def __create_functions_for_endpoints(self):
        """
        Create functions for endpoints to use needed schemas.
        :return: functions for endpoints
        """
        create_request_scheme = self.service.schemas.create_request_scheme
        update_request_scheme = self.service.schemas.update_request_scheme

        async def get_by_id(
            entity_id: int | str,
            user: CurrentUserDep = None,
            session: SessionDep = None,
        ):
            """
            Standard endpoint to get entity by it id
            :param id: id of entity
            :return: get_response_scheme object
            """
            entity = await self.service.get_entity_by_id(
                entity_id=entity_id, session=session, user=user
            )
            return BaseCrudRouter.map_from_db_object_to_scheme(
                entity, scheme=self.service.schemas.get_response_scheme
            )

        async def get_all_entities(
            user: CurrentUserDep,
            session: SessionDep,
        ):
            """
            Standard endpoint to all entities (you can add recursive_depth parameter - discussable)
            :return: list of get_response_scheme objects
            """
            query_parameters = None
            if user:
                query_parameters = self.service._parse_query_parameters(
                    organization_id=user.organization_id
                )

            db_entities = await self.service.get_all_entities(
                session=session, query_parameters=query_parameters
            )

            if db_entities is None:
                raise NotFoundException()

            return [
                self.map_from_db_object_to_scheme(
                    db_entity, scheme=self.service.schemas.get_response_scheme
                )
                for db_entity in db_entities
            ]

        async def delete_by_id(
            entity_id: int | str,
            user: CurrentUserDep,
            session: SessionDep,
        ):
            """
            Standard endpoint to delete entity by it id
            :param id: id of entity
            :return: JSONResponse(content=None)
            """
            await self.service.delete_entity_by_id(
                entity_id=entity_id, session=session, user=user
            )
            return JSONResponse(content=None)

        async def create_entity(
            entity: create_request_scheme,
            user: CurrentUserDep = None,
            session: SessionDep = None,
        ):
            """
            Standard endpoint to create entity (post method)
            :param entity: object of create_request_scheme class (it parsed with pydantic to needed schema)
            :return: get_response_scheme object
            """
            # Check if organization_id field exists in schema before setting
            if user and hasattr(entity, "organization_id"):
                entity.organization_id = user.organization_id
            entity_from_db = await self.service.create_entity(
                user=user, entity=entity, session=session
            )

            return BaseCrudRouter.map_from_db_object_to_scheme(
                db_object=entity_from_db,
                scheme=self.service.schemas.get_response_scheme,
            )

        async def update_entity(
            entity_id: int | str,
            entity: update_request_scheme,
            user: CurrentUserDep,
            session: SessionDep,
        ):
            """
            Standard endpoint to update entity
            :param id: id of entity to update
            :param entity: with what it should be updated - object of update_request_scheme class
            :return: get_response_scheme object
            """
            # Check if organization_id field exists in schema before setting
            if hasattr(entity, "organization_id"):
                entity.organization_id = user.organization_id
            entity_from_db = await self.service.update_entity(
                user=user, entity_id=entity_id, entity=entity, session=session
            )
            return BaseCrudRouter.map_from_db_object_to_scheme(
                entity_from_db, scheme=self.service.schemas.get_response_scheme
            )

        return get_by_id, get_all_entities, delete_by_id, create_entity, update_entity

    def __add_base_routes_to_self(self):
        """
        Private method to add standard endpoints in router (this class is router)
        Automatically get all standard funcs for endpoints (with self.__create_functions_for_endpoints())
        :return: None
        """
        get_by_id, get_all_entities, delete_by_id, create_entity, update_entity = (
            self.__create_functions_for_endpoints()
        )

        self.get_by_id_route = APIRoute(
            path="/{entity_id}",
            endpoint=get_by_id,
            methods=["GET"],
            tags=[self.tag],
            response_model=self.service.schemas.get_response_scheme,
        )
        self.get_all_entities_route = APIRoute(
            path="",
            endpoint=get_all_entities,
            methods=["GET"],
            tags=[self.tag],
            response_model=List[self.service.schemas.get_response_scheme],
        )
        self.delete_by_id_route = APIRoute(
            path="/{entity_id}",
            endpoint=delete_by_id,
            methods=["DELETE"],
            tags=[self.tag],
            response_class=JSONResponse,
        )
        self.create_route = APIRoute(
            path="",
            endpoint=create_entity,
            methods=["POST"],
            tags=[self.tag],
            response_model=self.service.schemas.get_response_scheme,
        )
        self.update_route = APIRoute(
            path="/{entity_id}",
            endpoint=update_entity,
            methods=["PATCH"],
            tags=[self.tag],
            response_model=self.service.schemas.get_response_scheme,
        )

        self.add_api_route_to_router(self.get_by_id_route)
        self.add_api_route_to_router(self.get_all_entities_route)
        self.add_api_route_to_router(self.delete_by_id_route)
        self.add_api_route_to_router(self.create_route)
        self.add_api_route_to_router(self.update_route)

    @staticmethod
    def map_from_db_object_to_scheme(db_object: object, scheme: BaseModel):
        """
        WARNING: Be sure that db_object has all fields that scheme want
        :param db_object: object from database (or json from recursive gets)
        :param scheme: scheme class to what you want to map object
        :return: dictionary mapped to needed scheme
        """
        if db_object is None:
            raise NotFoundException()

        if type(db_object) is dict:
            return {key: db_object.get(key) for key in scheme.model_fields.keys()}
        else:
            return {
                key: db_object.__dict__.get(key) for key in scheme.__fields__.keys()
            }

    @staticmethod
    def first_or_none(collection):
        first = None
        try:
            first = list(collection)[0]
        finally:
            return first
