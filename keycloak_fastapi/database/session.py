"""
Module for database session management.
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import event
from database.models import VSQLModel

from core.settings import load_settings


dbs = load_settings("DatabaseSettings")

engine = create_async_engine(
    dbs.url,
    echo=dbs.echo,
    pool_pre_ping=dbs.pool_pre_ping,
    pool_recycle=dbs.pool_recycle,
)

@event.listens_for(engine.sync_engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

AsyncSessionFactory = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async session.

    Yields:
        AsyncSession: An async session.
    """
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as error:
        await session.rollback()
        raise error
    finally:
        await session.close()


def init_db():
    VSQLModel.metadata.create_all(engine)