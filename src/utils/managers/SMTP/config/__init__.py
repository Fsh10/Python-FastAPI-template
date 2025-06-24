"""
Configuration for SMTP module.

This package contains configuration files for various email components:
- smtp_config.py - SMTP settings
- rabbitmq_config.py - RabbitMQ settings
- email_config.py - General email settings
"""

from .email_config import EmailConfig
from .rabbitmq_config import RabbitMQConfig
from .smtp_config import SMTPConfig

__all__ = ["SMTPConfig", "RabbitMQConfig", "EmailConfig"]
