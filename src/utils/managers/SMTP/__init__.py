"""
SMTP module for sending email without using Celery.

This module contains various ways to send email:
- Synchronous sending via SMTP
- Asynchronous sending
- Sending via RabbitMQ
- Scheduled sending via APScheduler
- Background tasks via FastAPI BackgroundTasks
"""

from .config import EmailConfig, RabbitMQConfig, SMTPConfig
from .config.email_config import email_config
from .config.rabbitmq_config import rabbitmq_config
from .config.smtp_config import smtp_config
from .routers import (
    async_router,
    info_router,
    rabbitmq_router,
    scheduled_router,
    sync_router,
)

__all__ = [
    # Sub-routers
    "sync_router",
    "async_router",
    "rabbitmq_router",
    "scheduled_router",
    "info_router",
    "SMTPConfig",
    "RabbitMQConfig",
    "EmailConfig",
    "smtp_config",
    "rabbitmq_config",
    "email_config",
]
