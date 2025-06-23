from fastapi import APIRouter
from starlette import status

from src.dependencies import CurrentUserDep
from src.utils.managers.SMTP.services.async_email_service import AsyncEmailService
from src.utils.managers.SMTP.SMTPSchemas import CustomMessageSchema
from src.utils.managers.SMTP.tasks.forms import Message_Form

async_router = APIRouter(prefix="/async", tags=["Email Async"])


@async_router.post("/send", tags=["Email Async"])
async def send_email_async(msg_info: CustomMessageSchema, user: CurrentUserDep):
    """
    Asynchronous email sending.
    """
    try:
        result = await AsyncEmailService.send_custom_email(
            subject=msg_info.subject,
            from_fio=msg_info.from_fio,
            to=msg_info.to,
            message=msg_info.message,
        )
        return {
            "message": "Email sent asynchronously",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@async_router.post("/send-bulk", tags=["Email Async"])
async def send_bulk_emails_async(emails_data: list[dict], user: CurrentUserDep):
    """
    Asynchronous bulk email sending.
    """
    try:
        emails = []
        for email_data in emails_data:
            email = Message_Form.form_custom_message(
                subject=email_data["subject"],
                from_fio=email_data["from_fio"],
                to=email_data["to"],
                message=email_data["message"],
            )
            emails.append(email)

        results = await AsyncEmailService.send_bulk_emails_with_semaphore(
            emails, max_concurrent=3
        )

        success_count = sum(results)
        total_count = len(results)

        return {
            "message": f"Sent {success_count} of {total_count} emails",
            "success_count": success_count,
            "total_count": total_count,
            "results": results,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@async_router.post("/send-registration", tags=["Email Async"])
async def send_registration_email_async(user_email: str, password: str):
    """
    Asynchronous registration email sending.
    """
    try:
        result = await AsyncEmailService.send_registration_email(user_email, password)
        return {
            "message": "Registration email sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@async_router.post("/send-password-reset", tags=["Email Async"])
async def send_password_reset_email_async(user_email: str, link: str):
    """
    Asynchronous password reset email sending.
    """
    try:
        result = await AsyncEmailService.send_password_reset_email(user_email, link)
        return {
            "message": "Password reset email sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@async_router.post("/send-alert", tags=["Email Async"])
async def send_alert_email_async(msg_info: dict):
    """
    Asynchronous alert email sending.
    """
    try:
        result = await AsyncEmailService.send_alert_email(
            level=msg_info["level"],
            message=msg_info["message"],
            ip=msg_info["ip"],
            source_timestamp=msg_info["source_timestamp"],
            name=msg_info["name"],
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


smtp_async_router = async_router
