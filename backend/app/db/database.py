"""
Async SQLAlchemy 2.x database engine and session factory.

All database I/O in Aegis is fully async using the asyncpg driver so that
no DB call ever blocks the FastAPI / uvicorn event loop.

Exports
-------
Base              — DeclarativeBase shared by all ORM models (db_models.py)
engine            — The async engine (used by init_db on startup)
AsyncSessionLocal — Session factory; use as an async context manager
get_db            — FastAPI dependency that yields a managed AsyncSession
init_db           — Called on application startup to create all tables
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# echo=True in dev logs every SQL statement — disable in production.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,   # recycle stale connections automatically
    pool_size=5,
    max_overflow=10,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# expire_on_commit=False keeps ORM objects usable after commit without an
# extra SELECT — important for background tasks that return quickly.
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Declarative Base — shared by ALL ORM models
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Common SQLAlchemy declarative base for all Aegis ORM models."""
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
async def get_db() -> AsyncSession:  # type: ignore[override]
    """
    Yield an ``AsyncSession`` for use as a FastAPI route dependency.

    Usage::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# Startup helper
# ---------------------------------------------------------------------------
async def init_db() -> None:
    """
    Create all tables defined on ``Base.metadata`` if they do not exist.

    Called from ``main.py``'s ``lifespan`` startup event so that the
    database schema is guaranteed to be present before the first request.

    In production, prefer running Alembic migrations instead of
    ``create_all`` to keep schema changes auditable and reversible.
    """
    logger.info("Initialising database schema…")
    try:
        async with engine.begin() as conn:
            # Import models here to ensure they are registered on Base.metadata
            # before create_all is called.
            from app.models import db_models  # noqa: F401  (side-effect import)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema ready.")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}. The app will run, but threat logs will not be persisted.")
