from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).parent
ENV_FILE = SRC_DIR / ".env"


class CeleryConfig(BaseSettings):
    # Redis settings
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    # Celery settings
    broker_url: str
    result_backend: str

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_prefix="CELERY_", extra="ignore")

    def get_broker_url(self) -> str:
        """Generate broker URL from components or use override"""
        if self.broker_url:
            return self.broker_url
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_result_backend_url(self) -> str:
        """Generate result backend URL from components or use override"""
        if self.result_backend:
            return self.result_backend
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_celery_config(self) -> dict:
        """Return all celery-specific configurations as a dictionary"""
        config = {
            "broker_url": self.get_broker_url(),
            "result_backend": self.get_result_backend_url(),
        }
        return config
