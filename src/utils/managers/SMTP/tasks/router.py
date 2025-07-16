from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import select
from starlette import status

from src.database import SessionLocal
from src.dependencies import CurrentUserDep
from src.users.UserModel import User
from src.utils.managers.SMTP.services.async_email_service import AsyncEmailService
from src.utils.managers.SMTP.services.email_service import EmailService
from src.utils.managers.SMTP.SMTPSchemas import AlertSchema, CustomMessageSchema

SMTP_router = APIRouter(prefix="/smtp")


@SMTP_router.post("/send_message", tags=["SMTP_router"])
async def send_cust_email(msg_info: CustomMessageSchema, user: CurrentUserDep) -> int:
    try:
        await AsyncEmailService.send_custom_email(
            subject=msg_info.subject,
            from_fio=msg_info.from_fio,
            to=msg_info.to,
            message=msg_info.message,
        )
        return 201
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@SMTP_router.post("/send_alert", tags=["SMTP_router"])
async def send_alert_email(msg_info: AlertSchema, user: CurrentUserDep) -> str:
    try:
        await AsyncEmailService.send_alert_email(
            from_fio=msg_info.name,
            to=user.email,
            message=msg_info.message,
            source_timestamp=msg_info.source_timestamp,
        )
        return "Alert sent successfully"
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@SMTP_router.post("/send_report", tags=["SMTP_router"])
async def send_report(user: CurrentUserDep):
    try:
        await AsyncEmailService.send_report_email(user.email)
        return {"message": "Report sent successfully"}
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


async def send_report():
    async with SessionLocal() as session:
        query = select(User.email).where(User.send_report == True)
        result = await session.execute(query)
        emails = result.scalars().all()
        for email in emails:
            await AsyncEmailService.send_report_email(email)
    return 201


@SMTP_router.post("/send_message_sync", tags=["SMTP_router"])
def send_cust_email_sync(msg_info: CustomMessageSchema, user: CurrentUserDep):
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


@SMTP_router.post("/send_message_async", tags=["SMTP_router"])
async def send_cust_email_async(msg_info: CustomMessageSchema, user: CurrentUserDep):
    """
    Asynchronous email sending without Celery.
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


@SMTP_router.post("/send_message_background", tags=["SMTP_router"])
def send_cust_email_background(
    msg_info: CustomMessageSchema,
    user: CurrentUserDep,
    background_tasks: BackgroundTasks,
):
    """
    Send email in background mode using BackgroundTasks.
    """

    def send_email_task():
        try:
            EmailService.send_custom_email(
                subject=msg_info.subject,
                from_fio=msg_info.from_fio,
                to=msg_info.to,
                message=msg_info.message,
            )
        except Exception as ex:
            pass

    background_tasks.add_task(send_email_task)
    return {
        "message": "Email added to background tasks queue"
    }, status.HTTP_202_ACCEPTED


@SMTP_router.post("/send_alert_sync", tags=["SMTP_router"])
def send_alert_email_sync(msg_info: AlertSchema, user: CurrentUserDep):
    """
    Synchronous alert sending without Celery.
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
            "message": "Alert sent",
            "success": result,
        }, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@SMTP_router.post("/send_report_sync", tags=["SMTP_router"])
def send_report_sync(user: CurrentUserDep):
    """
    Synchronous report sending without Celery.
    """
    try:
        result = EmailService.send_report_email(user.email)
        return {"message": "Report sent", "success": result}, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error sending: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
