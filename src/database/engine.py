from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app_config import get_settings


class DatabaseEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        engine = create_async_engine(get_settings().DATABASE_URL, connect_args={"ssl": get_settings().ssl_database_context})
        self.session_maker = async_sessionmaker(engine)
