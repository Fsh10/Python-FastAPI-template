from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest


class BaseTestCase:
    """Base class for all tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        self.setup_mocks()
        yield
        self.teardown()

    def setup_mocks(self):
        """Setup mocks."""
        self.mock_session = AsyncMock()
        self.mock_user = MagicMock()
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.organization_id = "org-123"

    def teardown(self):
        """Cleanup after test."""
        pass

    @pytest.fixture
    def mock_session(self):
        """Database session mock."""
        return self.mock_session

    @pytest.fixture
    def mock_user(self):
        """User mock."""
        return self.mock_user

    def assert_dict_contains(self, actual: Dict[str, Any], expected: Dict[str, Any]):
        """Check that dictionary contains expected keys and values."""
        for key, value in expected.items():
            assert key in actual, f"Key '{key}' is missing in result"
            assert actual[key] == value, f"Value for key '{key}' does not match"

    def assert_list_contains(self, actual_list: list, expected_item: Dict[str, Any]):
        """Check that list contains element with expected values."""
        found = False
        for item in actual_list:
            if all(item.get(key) == value for key, value in expected_item.items()):
                found = True
                break
        assert found, f"Element {expected_item} not found in list"

    def assert_error_response(
        self,
        response,
        expected_status_code: int,
        expected_error_type: Optional[str] = None,
    ):
        """Check error response."""
        assert response.status_code == expected_status_code
        if expected_error_type:
            data = response.json()
            assert "detail" in data
            if isinstance(data["detail"], str):
                assert expected_error_type in data["detail"]
            elif isinstance(data["detail"], list):
                assert any(
                    expected_error_type in str(error) for error in data["detail"]
                )


class BaseServiceTestCase(BaseTestCase):
    """Base class for service tests."""

    def setup_mocks(self):
        """Setup mocks for services."""
        super().setup_mocks()
        self.mock_repository = MagicMock()
        self.mock_schemas = MagicMock()

    @pytest.fixture
    def mock_repository(self):
        """Repository mock."""
        return self.mock_repository

    @pytest.fixture
    def mock_schemas(self):
        """Schemas mock."""
        return self.mock_schemas


class BaseRouterTestCase(BaseTestCase):
    """Base class for router tests."""

    def setup_mocks(self):
        """Setup mocks for routers."""
        super().setup_mocks()
        self.mock_service = MagicMock()

    @pytest.fixture
    def mock_service(self):
        """Service mock."""
        return self.mock_service


class BaseIntegrationTestCase(BaseTestCase):
    """Base class for integration tests."""

    def setup_mocks(self):
        """Setup mocks for integration tests."""
        super().setup_mocks()
        pass

    @pytest.fixture
    def test_data(self):
        """Base test data."""
        return {
            "user": {
                "email": "test@example.com",
                "password": "test_password",
                "organization_id": "org-123",
            },
        }
