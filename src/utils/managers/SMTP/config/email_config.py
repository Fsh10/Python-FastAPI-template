from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from src.config import settings


class EmailPriority(Enum):
    """Email priorities."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailType(Enum):
    """Email types."""

    CUSTOM = "custom_email"
    REGISTRATION = "registration_email"
    PASSWORD_RESET = "password_reset_email"
    ACCOUNT_ACTIVATION = "account_activation_email"
    ALERT = "alert_email"
    REPORT = "report_email"


@dataclass
class EmailConfig:
    """General email configuration."""

    default_priority: EmailPriority = EmailPriority.NORMAL
    default_charset: str = "utf-8"
    default_content_type: str = "text/html"
    default_from_name: str = settings.SMTP_USER
    default_from_email: str = settings.SMTP_USER

    max_recipients_per_email: int = 100
    allowed_domains: Optional[List[str]] = None

    max_subject_length: int = 255
    max_message_length: int = 1048576  # 1 MB
    allow_html: bool = True
    allow_attachments: bool = True
    max_attachment_size: int = 10485760  # 10 MB

    max_emails_per_minute: int = 60
    max_emails_per_hour: int = 1000
    max_emails_per_day: int = 10000

    max_scheduled_jobs: int = 1000
    default_schedule_timezone: str = "UTC"

    log_sent_emails: bool = True
    log_failed_emails: bool = True
    log_email_content: bool = False

    require_authentication: bool = True
    validate_email_addresses: bool = True
    block_suspicious_content: bool = True

    template_directory: str = "static/smtp/templates"
    default_template: str = "default.html"

    enable_admin_notifications: bool = True
    admin_email: str = settings.SMTP_USER

    def __post_init__(self):
        """Initialize after object creation."""
        if self.allowed_domains is None:
            self.allowed_domains = [
                "gmail.com",
                "yahoo.com",
                "hotmail.com",
                "outlook.com",
                settings.SMTP_USER,
            ]

    def is_domain_allowed(self, email: str) -> bool:
        """Check if email domain is allowed."""
        if not self.allowed_domains:
            return True

        domain = email.split("@")[-1].lower()
        return domain in [d.lower() for d in self.allowed_domains]

    def validate_email_address(self, email: str) -> bool:
        """Validate email address."""
        if not self.validate_email_addresses:
            return True

        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def validate_subject(self, subject: str) -> bool:
        """Validate email subject."""
        if not subject:
            return False

        if len(subject) > self.max_subject_length:
            return False

        return True

    def validate_message(self, message: str) -> bool:
        """Validate email message content."""
        if not message:
            return False

        if len(message) > self.max_message_length:
            return False

        return True

    def get_rate_limit_config(self) -> dict:
        """Get rate limit configuration."""
        return {
            "max_per_minute": self.max_emails_per_minute,
            "max_per_hour": self.max_emails_per_hour,
            "max_per_day": self.max_emails_per_day,
        }

    def get_logging_config(self) -> dict:
        """Get logging configuration."""
        return {
            "log_sent": self.log_sent_emails,
            "log_failed": self.log_failed_emails,
            "log_content": self.log_email_content,
        }

    def get_security_config(self) -> dict:
        """Get security configuration."""
        return {
            "require_auth": self.require_authentication,
            "validate_emails": self.validate_email_addresses,
            "block_suspicious": self.block_suspicious_content,
            "allowed_domains": self.allowed_domains,
        }

    def validate(self) -> bool:
        """Validate configuration."""
        if self.max_recipients_per_email <= 0:
            return False

        if self.max_subject_length <= 0:
            return False

        if self.max_message_length <= 0:
            return False

        if self.max_emails_per_minute <= 0:
            return False

        if self.max_emails_per_hour <= 0:
            return False

        if self.max_emails_per_day <= 0:
            return False

        return True


email_config = EmailConfig()
