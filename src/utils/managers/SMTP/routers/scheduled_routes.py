from fastapi import APIRouter
from starlette import status

from src.utils.managers.SMTP.services.scheduled_email_service import (
    scheduled_email_service,
)

scheduled_router = APIRouter(prefix="/scheduled", tags=["Email Scheduled"])


@scheduled_router.post("/immediate", tags=["Email Scheduled"])
def schedule_immediate_email(
    to: str, subject: str, message: str, delay_seconds: int = 0
):
    """
    Schedule immediate email sending with delay.
    """
    try:
        job_id = scheduled_email_service.schedule_immediate_email(
            to=to, subject=subject, message=message, delay_seconds=delay_seconds
        )
        return {
            "message": f"Email scheduled with delay of {delay_seconds} seconds",
            "job_id": job_id,
            "success": True,
        }, status.HTTP_201_CREATED
    except Exception as ex:
        return {
            "message": f"Error scheduling: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@scheduled_router.post("/daily", tags=["Email Scheduled"])
def schedule_daily_email(
    to: str, subject: str, message: str, hour: int = 9, minute: int = 0
):
    """
    Schedule daily email sending.
    """
    try:
        job_id = scheduled_email_service.schedule_daily_email(
            to=to, subject=subject, message=message, hour=hour, minute=minute
        )
        return {
            "message": f"Daily email scheduled for {hour:02d}:{minute:02d}",
            "job_id": job_id,
            "success": True,
        }, status.HTTP_201_CREATED
    except Exception as ex:
        return {
            "message": f"Error scheduling: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@scheduled_router.post("/weekly", tags=["Email Scheduled"])
def schedule_weekly_email(
    to: str,
    subject: str,
    message: str,
    day_of_week: int = 0,
    hour: int = 9,
    minute: int = 0,
):
    """
    Schedule weekly email sending.
    """
    try:
        job_id = scheduled_email_service.schedule_weekly_email(
            to=to,
            subject=subject,
            message=message,
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
        )
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        return {
            "message": f"Weekly email scheduled for {days[day_of_week]} at {hour:02d}:{minute:02d}",
            "job_id": job_id,
            "success": True,
        }, status.HTTP_201_CREATED
    except Exception as ex:
        return {
            "message": f"Error scheduling: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@scheduled_router.post("/interval", tags=["Email Scheduled"])
def schedule_interval_email(to: str, subject: str, message: str, hours: int = 24):
    """
    Schedule email sending with specified interval.
    """
    try:
        job_id = scheduled_email_service.schedule_interval_email(
            to=to, subject=subject, message=message, hours=hours
        )
        return {
            "message": f"Interval email scheduled every {hours} hours",
            "job_id": job_id,
            "success": True,
        }, status.HTTP_201_CREATED
    except Exception as ex:
        return {
            "message": f"Error scheduling: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@scheduled_router.delete("/{job_id}", tags=["Email Scheduled"])
def remove_scheduled_email(job_id: str):
    """
    Remove scheduled email.
    """
    try:
        result = scheduled_email_service.remove_job(job_id)
        if result:
            return {
                "message": "Scheduled email removed",
                "success": True,
            }, status.HTTP_200_OK
        else:
            return {
                "message": "Task not found",
                "success": False,
            }, status.HTTP_404_NOT_FOUND
    except Exception as ex:
        return {
            "message": f"Error removing: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@scheduled_router.get("/list", tags=["Email Scheduled"])
def get_scheduled_emails():
    """
    Get list of scheduled emails.
    """
    try:
        jobs = scheduled_email_service.get_all_jobs()
        return {"scheduled_emails": jobs, "total_count": len(jobs)}, status.HTTP_200_OK
    except Exception as ex:
        return {
            "message": f"Error getting list: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@scheduled_router.get("/{job_id}", tags=["Email Scheduled"])
def get_scheduled_email(job_id: str):
    """
    Get information about specific scheduled email.
    """
    try:
        job_info = scheduled_email_service.get_job(job_id)
        if job_info:
            return {"job": job_info, "success": True}, status.HTTP_200_OK
        else:
            return {
                "message": "Task not found",
                "success": False,
            }, status.HTTP_404_NOT_FOUND
    except Exception as ex:
        return {
            "message": f"Error getting information: {ex}",
            "success": False,
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


smtp_scheduled_router = scheduled_router
