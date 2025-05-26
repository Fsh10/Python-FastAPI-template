"""
Routers for email module.

This package contains separated routers for various types of email operations:
- sync_routes.py - Synchronous endpoints
- async_routes.py - Asynchronous endpoints
- rabbitmq_routes.py - RabbitMQ endpoints
- scheduled_routes.py - Scheduled endpoints
- info_routes.py - Information endpoints
"""

from .async_routes import async_router
from .info_routes import info_router
from .rabbitmq_routes import rabbitmq_router
from .scheduled_routes import scheduled_router
from .sync_routes import sync_router

__all__ = [
    "sync_router",
    "async_router",
    "rabbitmq_router",
    "scheduled_router",
    "info_router",
]
