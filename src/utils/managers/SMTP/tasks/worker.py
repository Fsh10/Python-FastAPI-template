import smtplib

from starlette import status

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready
from src.config import settings
from src.exceptions import InternalServerErrorException
from src.utils.managers.SMTP.tasks.forms import Message_Form

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

celery = Celery(
    __name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND
)
celery.conf.worker_autoscale = (10, 3)
celery.autodiscover_tasks()

celery.conf.update(
    timezone="Asia/Yekaterinburg",
    enable_utc=True,
    worker_hijack_root_logger=False,
    worker_log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    worker_task_log_format="%(asctime)s - %(name)s - %(levelname)s - %(task_name)s - %(task_id)s - %(message)s",
    worker_redirect_stdouts_level="INFO",
    worker_log_file="/fastapi/logs/celery_worker.log",
)

celery.conf.task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
        "durable": True,
    },
    "system": {
        "exchange": "system",
        "routing_key": "system",
        "durable": True,
    },
}

celery.conf.beat_schedule = {
    "delete_incorrect_patterns": {
        "task": "delete_incorrect_patterns",
        "schedule": crontab(day_of_week=0, hour=23, minute=00),
    },
}

celery.conf.task_default_delivery_mode = "persistent"
celery.conf.task_acks_late = True


def execute_smtp_task(task, *args, **kwargs):
    try:
        task_result = task.delay(*args, **kwargs).get()
        return {"message": task_result}, status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@worker_ready.connect
def on_worker_ready(sender=None, **kwargs):
    celery.control.enable_events()


@celery.task(
    name="send_email_for_registration_task",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def send_email_for_registration_task(user_email: str, password: str):
    try:
        email = Message_Form.form_reg_message_to_email(user_email, password)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@celery.task(
    name="form_account_activate_message_task",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def form_account_activate_message_task(user_email: str, link: str):
    try:
        email = Message_Form.form_account_activate_message_to_email(user_email, link)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@celery.task(
    name="form_reset_password_message_task",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def form_reset_password_message_task(user_email: str, link: str):
    try:
        email = Message_Form.form_reset_password_message_task(user_email, link)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@celery.task(
    name="send_alert_for_task",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def send_alert_for_task(level, message, ip, source_timestamp, name):
    try:
        email = Message_Form.form_alert(level, message, ip, source_timestamp, name)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@celery.task(
    name="create_task",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def send_email_smtp(user_email: str, password: str, message_type):
    try:
        email = message_type(user_email, password)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@celery.task(
    name="send_cust_email_smtp",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def send_cust_email_smtp(subject, from_fio, to, message):
    try:
        email = Message_Form.form_custom_message(subject, from_fio, to, message)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)


@celery.task(
    name="send_report_smtp",
    queue="default",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=3,
    retry_jitter=True,
)
def send_report_smtp(to):
    try:
        email = Message_Form.form_report_to_email(to)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
        return status.HTTP_201_CREATED
    except Exception as ex:
        raise InternalServerErrorException(error=ex)
