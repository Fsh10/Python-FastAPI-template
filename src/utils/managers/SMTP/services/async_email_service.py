import asyncio
import smtplib
from email.message import EmailMessage

from src.config import settings
from src.utils.managers.SMTP.tasks.forms import Message_Form


class AsyncEmailService:
    @staticmethod
    async def send_email_async(email: EmailMessage) -> bool:
        loop = asyncio.get_event_loop()

        def send():
            smtp_host = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
            smtp_port = getattr(settings, "SMTP_PORT", 465)
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(email)

        await loop.run_in_executor(None, send)
        return True

    @staticmethod
    async def send_password_reset_email(user_email: str, link: str) -> bool:
        email = Message_Form.form_reset_password_message_task(user_email, link)
        return await AsyncEmailService.send_email_async(email)

    @staticmethod
    async def send_custom_email(
        subject: str, from_fio: str, to: str, message: str
    ) -> bool:
        email = Message_Form.form_custom_message(subject, from_fio, to, message)
        return await AsyncEmailService.send_email_async(email)

    @staticmethod
    async def send_registration_email(user_email: str, password: str) -> bool:
        email = Message_Form.form_reg_message_to_email(user_email, password)
        return await AsyncEmailService.send_email_async(email)

    @staticmethod
    async def send_account_activate_email(user_email: str, link: str) -> bool:
        email = Message_Form.form_account_activate_message_to_email(user_email, link)
        return await AsyncEmailService.send_email_async(email)

    @staticmethod
    async def send_report_email(user_email: str) -> bool:
        email = Message_Form.form_report_to_email(user_email)
        return await AsyncEmailService.send_email_async(email)

    @staticmethod
    async def send_alert_email(
        from_fio: str, to: str, message: str, source_timestamp: str
    ) -> bool:
        email = Message_Form.form_alert(from_fio, to, message, source_timestamp)
        return await AsyncEmailService.send_email_async(email)
