from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config.db_config import db_settings

async_engine = create_async_engine(url=db_settings.DATABASE_URL, future=True, echo=True)

async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)
