from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class DatabaseEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5433/pulse")
        self.session_maker = async_sessionmaker(engine)
