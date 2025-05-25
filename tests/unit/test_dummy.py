"""
Dummy unit tests.
"""

import pytest

from tests.base.test_base import BaseTestCase


class TestDummyUnit(BaseTestCase):
    """Dummy unit tests."""

    @pytest.mark.unit
    def test_dummy_unit_pass(self):
        """Simple unit test that always passes."""
        assert True

    @pytest.mark.unit
    def test_dummy_unit_math(self):
        """Simple unit test with mathematical operations."""
        assert 1 + 1 == 2
        assert 2 * 2 == 4

    @pytest.mark.unit
    def test_dummy_unit_string(self):
        """Simple unit test with strings."""
        assert "hello" == "hello"
        assert len("test") == 4

