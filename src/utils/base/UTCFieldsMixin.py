"""
Mixin for automatic UTC formatting of model fields.
"""

from typing import Any

from sqlalchemy import event

from src.utils.managers import time_manager


class UTCFieldsMixin:
    """
    Mixin for automatic UTC formatting of model fields.

    Automatically converts all datetime fields to UTC when saving to DB
    and validates them when loading from DB.
    """

    UTC_DATETIME_FIELDS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ensure_utc_fields()

    def _ensure_utc_fields(self):
        """Ensure that all datetime fields are in UTC."""
        for field_name in self.UTC_DATETIME_FIELDS:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    utc_value = time_manager.force_utc_datetime(value)
                    setattr(self, field_name, utc_value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Intercept attribute setting for automatic UTC conversion."""
        if name in self.UTC_DATETIME_FIELDS and value is not None:
            value = time_manager.force_utc_datetime(value)

        super().__setattr__(name, value)

    def validate_utc_fields(self) -> None:
        """Validate that all datetime fields are in UTC."""
        for field_name in self.UTC_DATETIME_FIELDS:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    time_manager.validate_utc_datetime(value, field_name)


def register_utc_events(model_class):
    """
    Register SQLAlchemy events for automatic UTC formatting.

    Args:
        model_class: Model class to register events for.
    """

    @event.listens_for(model_class, "before_insert")
    def before_insert(mapper, connection, target):
        """Before insert - convert all datetime fields to UTC."""
        if hasattr(target, "UTC_DATETIME_FIELDS"):
            for field_name in target.UTC_DATETIME_FIELDS:
                if hasattr(target, field_name):
                    value = getattr(target, field_name)
                    if value is not None:
                        utc_value = time_manager.force_utc_datetime(value)
                        setattr(target, field_name, utc_value)

    @event.listens_for(model_class, "before_update")
    def before_update(mapper, connection, target):
        """Before update - convert all datetime fields to UTC."""
        if hasattr(target, "UTC_DATETIME_FIELDS"):
            for field_name in target.UTC_DATETIME_FIELDS:
                if hasattr(target, field_name):
                    value = getattr(target, field_name)
                    if value is not None:
                        utc_value = time_manager.force_utc_datetime(value)
                        setattr(target, field_name, utc_value)

    @event.listens_for(model_class, "load")
    def after_load(target, context):
        """After load - validate that all datetime fields are in UTC."""
        if hasattr(target, "UTC_DATETIME_FIELDS"):
            for field_name in target.UTC_DATETIME_FIELDS:
                if hasattr(target, field_name):
                    value = getattr(target, field_name)
                    if value is not None:
                        time_manager.validate_utc_datetime(value, field_name)


def utc_datetime_field(*field_names: str):
    """
    Decorator for automatic UTC field definition in model.

    Args:
        *field_names: Field names that should be in UTC.
    """

    def decorator(cls):
        if not hasattr(cls, "UTC_DATETIME_FIELDS"):
            cls.UTC_DATETIME_FIELDS = []

        cls.UTC_DATETIME_FIELDS.extend(field_names)
        register_utc_events(cls)

        return cls

    return decorator
