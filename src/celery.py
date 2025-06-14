"""
Celery application entry point.
Imports celery from worker.py for compatibility with commands in justfile.
"""

from src.utils.managers.SMTP.tasks.worker import celery

__all__ = ["celery"]
