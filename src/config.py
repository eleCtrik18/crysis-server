import os
from dotenv import load_dotenv

from pathlib import Path
from kombu import Queue
from celery.schedules import crontab


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    ENV: str = os.getenv("ENV", "development")
    PROJECT_NAME: str = "aura"
    PROJECT_VERSION: str = "0.1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_CLUSTER_MODE: str = os.getenv("REDIS_CLUSTER_MODE", "0")
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days
    ALGORITHM = "HS256"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")  # should be kept secret
    JWT_REFRESH_SECRET_KEY = os.getenv(
        "JWT_REFRESH_SECRET_KEY", ""
    )  # should be kept secret
    AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
    PARTNER_JWT_SECRET_KEY = os.getenv("PARTNER_JWT_SECRET_KEY")
    CAMSPAY_CREDENTIALS = {
        "CAMSPAY_ENCRYPTION_KEY": os.getenv("CAMSPAY_ENCRYPTION_KEY"),
        "MERCHANT_ID": os.getenv("MERCHANT_ID"),
        "SUBBILLER_ID": os.getenv("SUBBILLER_ID"),
        "CAMSPAY_ID": os.getenv("CAMSPAY_ID"),
        "URL_HOST": os.getenv("URL_HOST"),
    }
    AURA_HOST = os.getenv("AURA_HOST")
    REDIS_URL = os.getenv("REDIS_URL")
    MOIHOST_URL = os.getenv("MOIHOST_URL")
    MOIAPI_SECRET_KEY = os.getenv("MOIAPI_SECRET_KEY")
    IDFY_REQ_URL =  os.getenv("IDFY_REQ_URL")
    IDFY_REQ_TEST_URL = os.getenv("IDFY_REQ_TEST_URL")
    IDFY_VERIFY_URL = os.getenv("IDFY_VERIFY_URL")
    IDFY_VERIFY_TEST_URL = os.getenv("IDFY_VERIFY_TEST_URL") 
    IDFY_KEY = os.getenv("IDFY_KEY")
    IDFY_ACC = os.getenv("IDFY_ACC")
    IDFY_GROUP_ID = os.getenv("IDFY_GROUP_ID")


class CeleryConfig:
    broker_url: str = os.getenv("CELERY_broker_url")
    result_backend: str = os.getenv("CELERY_result_backend", "redis://127.0.0.1:6379/0")

    task_default_queue: str = "default"

    task_create_missing_queues: bool = True

    task_queues: list = [
        # need to define default queue here or exception would be raised
        Queue("default"),
        Queue("high_priority"),
        Queue("low_priority"),
    ]
    beat_schedule: dict = {
        "run_gold_updater": {
            "task": "run_gold_updater",
            "schedule": crontab(minute="*/10"),  # every ten minutes
        },
        "run_mandate_notification_sender": {
            "task": "run_mandate_notification_sender",
            "schedule": crontab(minute="*/10"),  # every 10 minutes
        },
        "run_update_pending_mandates": {
            "task": "run_update_pending_mandates",
            "schedule": crontab(minute="*/20"),  # every twenty minutes
        },
        "run_execute_mandates": {
            "task": "run_execute_mandates",
            "schedule": crontab(minute="*/20"),  # every 10 minutes
        },
        "run_update_mandate_transaction_status": {
            "task": "run_update_mandate_transaction_status",
            "schedule": crontab(minute="*/10"),  # every 10 minutes
        },
        "run_check_and_credit_gold": {
            "task": "run_check_and_credit_gold",
            "schedule": crontab(minute="*/30"),  # every 10 minutes
        },
    }
    imports = "src.tasks"
    broker_connection_retry_on_startup = True
    timezone = "Asia/Kolkata"
    # redis_max_connections = 20  # Adjust this value as needed
    # redis_socket_timeout = 60


settings = Settings()
celery_settings = CeleryConfig()
