from dataclasses import dataclass

from src.config import settings


@dataclass
class SMTPConfig:
    """SMTP server configuration."""

    host: str = "smtp.gmail.com"
    port: int = 465
    use_ssl: bool = True
    use_tls: bool = False

    username: str = settings.SMTP_USER
    password: str = settings.SMTP_PASSWORD

    from_email: str = settings.SMTP_USER
    from_name: str = "FastAPI Template System"

    timeout: int = 30
    connection_timeout: int = 10

    require_auth: bool = True
    verify_ssl: bool = True

    max_retries: int = 3
    retry_delay: int = 5

    max_concurrent_connections: int = 5
    max_messages_per_connection: int = 100

    @classmethod
    def from_settings(cls) -> "SMTPConfig":
        """Create configuration from application settings."""
        return cls(
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            from_email=settings.SMTP_USER,
        )

    def get_connection_params(self) -> dict:
        """Get SMTP connection parameters."""
        return {
            "host": self.host,
            "port": self.port,
            "timeout": self.timeout,
            "use_ssl": self.use_ssl,
            "use_tls": self.use_tls,
        }

    def get_auth_params(self) -> dict:
        """Get authentication parameters."""
        return {"username": self.username, "password": self.password}

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.username or not self.password:
            return False

        if self.port <= 0 or self.port > 65535:
            return False

        if self.timeout <= 0:
            return False

        return True


smtp_config = SMTPConfig.from_settings()
