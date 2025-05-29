"""
Dummy integration tests.
"""

import pytest

from tests.base.test_base import BaseIntegrationTestCase


class TestDummyIntegration(BaseIntegrationTestCase):
    """Dummy integration tests."""

    @pytest.mark.integration
    def test_dummy_integration_pass(self):
        """Simple integration test that always passes."""
        assert True

    @pytest.mark.integration
    def test_dummy_integration_data(self):
        """Simple integration test with test data."""
        test_data = self.test_data
        assert "user" in test_data
        assert test_data["user"]["email"] == "test@example.com"

    @pytest.mark.integration
    def test_dummy_integration_mocks(self):
        """Simple integration test with mocks."""
        assert self.mock_session is not None
        assert self.mock_user is not None

