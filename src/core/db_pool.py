import traceback
from venv import logger
from typing import Optional
from src.core import db_models
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select
from src.core.variables import DATABASE_URL


def initDB(_engine):
    try:
        SQLModel.metadata.create_all(_engine)
        print("DB initialized")
    except:
        traceback.print_exc()
        print(f"Error in creating init tables.")


class UninitializedDatabasePoolError(Exception):
    def __init__(
        self,
        message="The database connection pool has not been properly initialized. Please ensure setup is called",
    ):
        self.message = message
        super().__init__(self.message)


class DataBasePool:
    """Manages database connection pool using SQLModel."""

    _instance = None
    _engine = None
    _db_pool: Session = None

    @classmethod
    async def initDB(cls):
        initDB(cls._engine)

    @classmethod
    async def getEngine(cls):
        return cls._engine

    @classmethod
    async def setup(cls, timeout: Optional[float] = None):
        if cls._engine == None:
            cls._engine = create_engine(
                DATABASE_URL,
                pool_size=20,  # Maximum number of connections
                max_overflow=10,  # Extra connections when pool maxed
                pool_timeout=30,  # Seconds to wait for connection
                pool_recycle=300,  # Recycle connections after 30 mins
                pool_pre_ping=True,  # Verify connection is valid
                echo=False,
            )
            initDB(cls._engine)
            cls._timeout = timeout
            with Session(cls._engine) as session:
                cls._db_pool = session
    @classmethod
    def sync_setup(cls, timeout: Optional[float] = None):
        if cls._engine == None:
            cls._engine = create_engine(
                DATABASE_URL,
                pool_size=20,  # Maximum number of connections
                max_overflow=10,  # Extra connections when pool maxed
                pool_timeout=30,  # Seconds to wait for connection
                pool_recycle=1800,  # Recycle connections after 30 mins
                pool_pre_ping=True,  # Verify connection is valid
                echo=False,
            )
            initDB(cls._engine)
            cls._timeout = timeout
            with Session(cls._engine) as session:
                cls._db_pool = session
    @classmethod
    def get_pool(cls) -> Session:
        if not cls._db_pool:
            raise UninitializedDatabasePoolError()
        return cls._db_pool

    @classmethod
    async def teardown(cls):
        logger.info(f"Closing db_pool")
        if not cls._db_pool:
            raise UninitializedDatabasePoolError()

        # Verify connection health
        if not await cls.verify_connection(cls._db_pool):
            logger.warning("Unhealthy connection detected, creating new session")
            with Session(cls._engine) as session:
                cls._db_pool = session
        else:
            cls._db_pool.close()
            logger.info(f"db_pool closed")

    @classmethod
    async def verify_connection(cls, db_pool: Session) -> bool:
        try:
            statement = select(1)
            db_pool.exec(statement).first()
            return True
        except Exception as e:
            logger.error(f"Connection verification failed: {str(e)}")
            return False
