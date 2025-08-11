from fastapi import APIRouter
from starlette import status

from src.dependencies import CurrentUserDep
from src.utils.managers.SMTP.services.email_service import EmailService
from src.utils.managers.SMTP.SMTPSchemas import AlertSchema, CustomMessageSchema

sync_router = APIRouter(prefix="/sync", tags=["Email Sync"])


@sync_router.post("/send", tags=["Email Sync"])
def send_email_sync(msg_info: CustomMessageSchema, user: CurrentUserDep):
    """
    Synchronous email sending without Celery.
    """
    try:
        result = EmailService.send_custom_email(
            subject=msg_info.subject,
            from_fio=msg_info.from_fio,
            to=msg_info.to,
            message=msg_info.message,
        )
        return {
            "message": "Email sent synchronously",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@sync_router.post("/send-registration", tags=["Email Sync"])
def send_registration_email_sync(user_email: str, password: str):
    """
    Synchronous registration email sending.
    """
    try:
        result = EmailService.send_registration_email(user_email, password)
        return {
            "message": "Registration email sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@sync_router.post("/send-password-reset", tags=["Email Sync"])
def send_password_reset_email_sync(user_email: str, link: str):
    """
    Synchronous password reset email sending.
    """
    try:
        result = EmailService.send_password_reset_email(user_email, link)
        return {
            "message": "Password reset email sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@sync_router.post("/send-alert", tags=["Email Sync"])
def send_alert_email_sync(msg_info: AlertSchema, user: CurrentUserDep):
    """
    Synchronous alert email sending.
    """
    try:
        result = EmailService.send_alert_email(
            level=msg_info.level,
            message=msg_info.message,
            ip=msg_info.ip,
            source_timestamp=msg_info.source_timestamp,
            name=msg_info.name,
        )
        return {
            "message": "Alert email sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@sync_router.post("/send-report", tags=["Email Sync"])
def send_report_email_sync(user: CurrentUserDep):
    """
    Synchronous report email sending.
    """
    try:
        result = EmailService.send_report_email(user.email)
        return {
            "message": "Report email sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


smtp_sync_router = sync_router
