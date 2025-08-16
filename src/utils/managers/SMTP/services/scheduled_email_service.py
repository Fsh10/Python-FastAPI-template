import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config import settings
from src.utils.managers.SMTP.services.async_email_service import AsyncEmailService


class ScheduledEmailService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def schedule_immediate_email(
        self, to: str, subject: str, message: str, delay_seconds: int = 0
    ) -> str:
        run_date = datetime.now() + timedelta(seconds=delay_seconds)
        job_id = f"email_{uuid.uuid4()}"
        self.scheduler.add_job(
            self._send_email_task,
            trigger=DateTrigger(run_date=run_date),
            args=[to, subject, message],
            id=job_id,
        )
        return job_id

    def schedule_daily_email(
        self, to: str, subject: str, message: str, hour: int = 9, minute: int = 0
    ) -> str:
        job_id = f"daily_email_{uuid.uuid4()}"
        self.scheduler.add_job(
            self._send_email_task,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[to, subject, message],
            id=job_id,
        )
        return job_id

    def schedule_weekly_email(
        self,
        to: str,
        subject: str,
        message: str,
        day_of_week: int = 0,
        hour: int = 9,
        minute: int = 0,
    ) -> str:
        job_id = f"weekly_email_{uuid.uuid4()}"
        self.scheduler.add_job(
            self._send_email_task,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            args=[to, subject, message],
            id=job_id,
        )
        return job_id

    def schedule_interval_email(
        self, to: str, subject: str, message: str, hours: int = 24
    ) -> str:
        job_id = f"interval_email_{uuid.uuid4()}"
        self.scheduler.add_job(
            self._send_email_task,
            trigger=IntervalTrigger(hours=hours),
            args=[to, subject, message],
            id=job_id,
        )
        return job_id

    def remove_job(self, job_id: str) -> bool:
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception:
            return False

    def get_job(self, job_id: str) -> Optional[Dict]:
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        return {
            "id": job.id,
            "trigger": str(job.trigger),
            "next_run_time": str(job.next_run_time),
        }

    def get_all_jobs(self) -> List[Dict]:
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "trigger": str(job.trigger),
                "next_run_time": str(job.next_run_time),
            }
            for job in jobs
        ]

    def shutdown(self):
        self.scheduler.shutdown(wait=False)

    async def _send_email_task(self, to: str, subject: str, message: str):
        try:
            await AsyncEmailService.send_custom_email(
                subject=subject, from_fio=settings.SMTP_USER, to=to, message=message
            )
        except Exception as ex:
            logger.error(f"Error sending email: {ex}")


scheduled_email_service = ScheduledEmailService()
