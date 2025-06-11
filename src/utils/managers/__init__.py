"""
Managers for working with various services and utilities.
"""

from .RabbitMQ.EmailService import RabbitMQEmailService, email_rabbitmq_service
from .S3.connection import (
    S3_CLIENT,
    S3_CLIENT_STATIC_BACKEND,
    S3Client,
)
from .S3.FileManager import FileManager
from .time_manager import TimeManager, time_manager

__all__ = [
    "TimeManager",
    "time_manager",
    "FileManager",
    "S3Client",
    "S3_CLIENT",
    "S3_CLIENT_STATIC_BACKEND",
    "RabbitMQEmailService",
    "email_rabbitmq_service",
]
