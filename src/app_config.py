import os
import ssl
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

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

    # API Keys
    ANTHROPIC_API_KEY: str
    PINECONE_API_KEY: str
    VOYAGEAI_API_KEY: str
    CRYPTO_PANIC_API_KEY: str

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")

    @property
    def DATABASE_URL(self) -> str:
        conn_str = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return conn_str

    @property
    def ssl_database_context(self):
        # Define file paths for temporary files
        server_ca_path = "./server_ca.crt"
        client_cert_path = "./client_cert.crt"
        client_key_path = "./client_key.key"

        # # Write the environment variable content to files with restricted permissions
        # def write_cert_file(path: str, content: str):
        #     with open(path, "w") as f:
        #         os.fchmod(f.fileno(), 0o600)  # Set permissions to -rw-------
        #         f.write(content)
        #
        # write_cert_file(server_ca_path, self.PGSSLROOTCERT_CONTENT)
        # write_cert_file(client_cert_path, self.PGSSLCERT_CONTENT)
        # write_cert_file(client_key_path, self.PGSSLKEY_CONTENT)

        sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_ca_path)
        sslctx.check_hostname = False
        sslctx.load_cert_chain(client_cert_path, keyfile=client_key_path)

        return sslctx


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
