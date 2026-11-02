from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one database session for the duration of an API request."""

    async with session_factory() as session:
        yield session


async def check_database_connection() -> None:
    """Raise when PostgreSQL cannot accept a lightweight query."""

    async with engine.connect() as connection:
        await connection.exec_driver_sql("SELECT 1")
