from celery import Celery

celery_app = Celery(
    "bookstore",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.task_track_started = True
celery_app.conf.result_backend = "redis://localhost:6379/0"
