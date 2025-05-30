from typing import AsyncGenerator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

if settings.MODE == "TEST":
    DATABASE_URL = str(settings.DATABASE_URL_TEST)
else:
    DATABASE_URL = str(settings.DATABASE_ASYNC_URL)

Base = declarative_base()

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    pool_timeout=30,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

sync_engine = create_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    pool_timeout=30,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
sync_session_maker = sessionmaker(sync_engine, expire_on_commit=False)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        await session.commit()
        await session.close()


def get_sync_session():
    with sessionmaker() as session:
        yield session


async def close_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
