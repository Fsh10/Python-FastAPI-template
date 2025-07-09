import os
from datetime import datetime
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import settings
from src.dependencies import get_static_path


class Message_Form:
    @classmethod
    def form_reg_message_to_email(cls, user_email: str, password: str):
        email = EmailMessage()
        email["Subject"] = "Registration on the portal."
        email["From"] = settings.SMTP_USER
        email["To"] = user_email

        email.set_content(
            "<div>"
            "<h2>Hello! You have registered on the FastAPI Template "
            "production process management portal.</h2>"
            f"<h3>Your login credentials for the portal:</h3>"
            f"<h3>Your login: {user_email}</h3>"
            f"<h3>Your password: {password}</h3>"
            "<h4>If you received this message by mistake, please ignore it.</h4>"
            "</div>",
            subtype="html",
        )
        return email

    @classmethod
    def form_reset_password_message_task(cls, user_email: str, link: str):
        email = EmailMessage()
        email["Subject"] = "Password reset on fastapi-template.com portal"
        email["From"] = settings.SMTP_USER
        email["To"] = user_email

        file_path = os.path.join(get_static_path(), "smtp", "reset_password.html")

        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read().replace("<!--insert link here-->", link)

        email.set_content(html_content, subtype="html")
        return email

    @classmethod
    def form_account_activate_message_to_email(cls, user_email: str, link: str):
        email = EmailMessage()
        email["Subject"] = "Account activation on FastAPI Template"
        email["From"] = settings.SMTP_USER
        email["To"] = user_email

        file_path = os.path.join(get_static_path(), "smtp", "verify_message.html")

        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        html_content = html_content.replace("<!--insert link here-->", link)

        email.set_content(html_content, subtype="html")
        return email

    @classmethod
    def form_report_to_email(cls, user_email: str):
        email = MIMEMultipart()
        email["Subject"] = "Report from FastAPI Template Backend"
        email["From"] = settings.SMTP_USER
        email["To"] = user_email

        body = MIMEText(
            "Hello, you requested a report on the FastAPI Template platform. It is attached.",
            "plain",
        )
        email.attach(body)

        file_name = datetime.now().strftime("%d.%m.%Y") + ".xlsx"
        file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "smtp", file_name)
        )

        with open(file_path, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
        part["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(file_path)}"'
        )
        email.attach(part)

        return email

    @classmethod
    def form_custom_message(cls, subject, from_fio, to, message):
        email = EmailMessage()
        email["Subject"] = subject
        email["From"] = from_fio
        email["To"] = to

        email.set_content(f"<div>{message}</div>", subtype="html")
        return email

    @classmethod
    def form_alert(cls, from_fio, to, message, source_timestamp):
        email = EmailMessage()
        email["Subject"] = message
        email["From"] = from_fio
        email["To"] = to

        email.set_content(
            f"<div>Attention! {source_timestamp} on device, {message}</div>",
            subtype="html",
        )
        return email
