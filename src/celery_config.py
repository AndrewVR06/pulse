from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_config import get_settings

SRC_DIR = Path(__file__).parent
ENV_FILE = SRC_DIR / ".env"


class CeleryConfig(BaseSettings):

    # Celery settings
    broker_url: str
    result_backend: str

    # Worker settings
    worker_prefetch_multiplier: int = Field(default=1)
    worker_max_tasks_per_child: int = Field(default=1)  # Die after one task
    worker_concurrency: int = Field(default=1)  # Process one task at a time

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_prefix="CELERY_", extra="ignore")

    def get_broker_url(self) -> str:
        """Generate broker URL from components or use override"""
        if self.broker_url:
            return self.broker_url
        return get_settings().redis_url

    def get_result_backend_url(self) -> str:
        """Generate result backend URL from components or use override"""
        if self.result_backend:
            return self.result_backend
        return get_settings().redis_url

    def get_celery_config(self) -> dict:
        """Return all celery-specific configurations as a dictionary"""
        config = {
            "broker_url": self.get_broker_url(),
            "result_backend": self.get_result_backend_url(),
            # Worker settings
            "worker_prefetch_multiplier": self.worker_prefetch_multiplier,
            "worker_max_tasks_per_child": self.worker_max_tasks_per_child,
            # Logging settings
            "worker_log_format": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
            "worker_task_log_format": ("[%(asctime)s: %(levelname)s/%(processName)s] " "[%(task_name)s(%(task_id)s)] %(message)s"),
        }
        return config


@lru_cache
def get_celery_config() -> CeleryConfig:
    return CeleryConfig()
