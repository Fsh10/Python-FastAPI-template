import smtplib
from email.message import EmailMessage

from src.config import settings
from src.utils.managers.SMTP.tasks.forms import Message_Form


class EmailService:
    @staticmethod
    def send_email(email: EmailMessage) -> bool:
        """Synchronous email sending via SMTP."""
        try:
            smtp_host = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
            smtp_port = getattr(settings, "SMTP_PORT", 465)
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(email)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def send_password_reset_email(user_email: str, link: str) -> bool:
        """Send password reset email."""
        email = Message_Form.form_reset_password_message_task(user_email, link)
        return EmailService.send_email(email)

    @staticmethod
    def send_custom_email(subject: str, from_fio: str, to: str, message: str) -> bool:
        """Send custom email."""
        email = Message_Form.form_custom_message(subject, from_fio, to, message)
        return EmailService.send_email(email)

    @staticmethod
    def send_registration_email(user_email: str, password: str) -> bool:
        """Send registration email."""
        email = Message_Form.form_reg_message_to_email(user_email, password)
        return EmailService.send_email(email)

    @staticmethod
    def send_account_activate_email(user_email: str, link: str) -> bool:
        """Send account activation email."""
        email = Message_Form.form_account_activate_message_to_email(user_email, link)
        return EmailService.send_email(email)

    @staticmethod
    def send_report_email(user_email: str) -> bool:
        """Send report email."""
        email = Message_Form.form_report_to_email(user_email)
        return EmailService.send_email(email)

    @staticmethod
    def send_alert_email(
        level: str, message: str, ip: str, source_timestamp: str, name: str
    ) -> bool:
        """Send alert email."""
        email = Message_Form.form_alert(name, name, message, source_timestamp)
        return EmailService.send_email(email)
