from unittest.mock import AsyncMock, MagicMock, Mock

from pydantic import BaseModel


class BaseRepositoryForTests:
    model = MagicMock()

    def __init__(self):
        self._execute_query = AsyncMock()
        self._execute_query_scalar_all = AsyncMock(return_value=[Mock(), Mock()])
        self.create_entity_in_db = AsyncMock(return_value={"id": 1, "name": "Entity"})
        self.get_entity_from_db_by_id = AsyncMock(
            return_value={"id": 1, "name": "Entity"}
        )
        self.get_all_entities_from_db = AsyncMock(
            return_value=[{"id": 1, "name": "Entity"}]
        )
        self.update_entity_in_db = AsyncMock(
            return_value={"id": 1, "name": "Entity Updated"}
        )
        self.delete_entity_from_db_by_id = AsyncMock(return_value=True)
        self.get_all_filtered_entities_from_db = AsyncMock(
            return_value=[{"id": 1, "name": "Entity"}]
        )
        self.get_all_entity_ids = AsyncMock(return_value=["id1", "id2"])


class BaseServiceForTests:
    class Model(BaseModel):
        id: int
        name: str

    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock())
    user = Mock()
    repository = BaseRepositoryForTests()
    schemas = Mock()
    schemas.get_response_scheme = Mock(return_value=Model(id=1, name="Entity"))

    async def test_create_entity(self):
        data = MagicMock(return_value={"name": "Entity"})
        data.model_dump = MagicMock()
        result = await self.service.create_entity(
            entity=data, user=self.user, session=self.session
        )
        self.repository.create_entity_in_db.assert_called_once_with(
            entity=data, session=self.session
        )
        self.assertEqual(result, self.schemas.get_response_scheme())

    async def test_get_entity_by_id(self):
        result = await self.service.get_entity_by_id(
            entity_id=1, session=self.session, user=self.user
        )
        self.repository.get_entity_from_db_by_id.assert_called_once_with(
            entity_id=1, session=self.session
        )
        self.assertEqual(result, self.schemas.get_response_scheme())

    async def test_get_all_entities(self):
        result = await self.service.get_all_entities(session=self.session)
        self.repository.get_all_entities_from_db.assert_called_once()
        self.assertIsInstance(result, list)

    async def test_get_all_filtered_entities(self):
        query_parameters = {"name": "Entity"}
        result = await self.service.get_all_filtered_entities(
            query_parameters=query_parameters, session=self.session
        )
        self.repository.get_all_filtered_entities_from_db.assert_called_once_with(
            query_parameters=query_parameters, session=self.session, recursive_depth=4
        )
        self.assertIsInstance(result, list)

    async def test_update_entity(self):
        data = MagicMock(return_value={"name": "Entity Updated"})
        result = await self.service.update_entity(
            entity_id=1, entity=data, user=self.user, session=self.session
        )
        self.repository.update_entity_in_db.assert_called_once_with(
            entity_id=1, entity=data, session=self.session
        )
        self.assertEqual(result, self.schemas.get_response_scheme())

    async def test_delete_entity_by_id(self):
        result = await self.service.delete_entity_by_id(
            entity_id=1, user=self.user, session=self.session
        )
        self.repository.delete_entity_from_db_by_id.assert_called_once_with(
            entity_id=1, session=self.session
        )
        self.assertIsNone(result)
