import os
import ssl
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache, cached_property

SRC_DIR = Path(__file__).parent
ENV_FILE = SRC_DIR / ".env"


class AppSettings(BaseSettings):

    # Application settings
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "local"

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    PGSSLROOTCERT_CONTENT: str | None = None
    PGSSLCERT_CONTENT: str | None = None
    PGSSLKEY_CONTENT: str | None = None

    # Redis settings
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_URL: Optional[str] = Field(default="")

    # API Keys
    ANTHROPIC_API_KEY: str
    PINECONE_API_KEY: str
    VOYAGEAI_API_KEY: str
    CRYPTO_PANIC_API_KEY: str

    # Twilio Keys
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")

    @cached_property
    def DATABASE_URL(self) -> str:
        conn_str = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return conn_str

    @cached_property
    def ssl_database_context(self):
        # Define file paths for temporary files
        server_ca_path = "./server_ca.crt"
        client_cert_path = "./client_cert.crt"
        client_key_path = "./client_key.key"

        sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_ca_path)
        sslctx.check_hostname = False
        sslctx.load_cert_chain(client_cert_path, keyfile=client_key_path)

        return sslctx

    @cached_property
    def redis_url(self) -> str:
        """Return the redis host"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
