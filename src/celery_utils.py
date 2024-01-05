from src.config import celery_settings
from celery import current_app as current_celery_app, shared_task


def create_celery_app():
    celery_app = current_celery_app
    celery_app.config_from_object(celery_settings)

    return celery_app
