from celery import Celery
from src.core.variables import REDIS_URL
from celery.schedules import crontab

celery_app = Celery(
    "gemini_backend_message_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.celery.service"],
)

celery_app.conf.update(
    task_routes={
        "send_gemini_message": {"queue": "send_gemini_message"},
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_prefetch_multiplier=1,  # One task per worker
    result_expires=86400 * 7,  # Expires in 7 day
    task_acks_late=True,  # Tasks acknowledged after execution
    task_reject_on_worker_lost=True,  # Reject tasks if worker disconnects
    task_track_started=True,
    task_send_sent_event=True,
    worker_max_tasks_per_child=1000,  # after 1000 taks worker will restart
    broker_connection_retry_on_startup=True,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s] %(message)s",
)

celery_app.conf.timezone = "Asia/Kolkata"
celery_app.conf.enable_utc = False
