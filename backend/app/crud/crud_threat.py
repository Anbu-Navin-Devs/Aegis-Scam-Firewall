"""
CRUD operations for the ThreatLog table.

All functions accept an ``AsyncSession`` and are fully async so they
compose cleanly with FastAPI's dependency-injection system and
``asyncio.create_task`` fire-and-forget patterns.
"""

from __future__ import annotations

import logging
from typing import Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ThreatLog

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

async def create_threat_log(db: AsyncSession, log_data: dict) -> ThreatLog:
    """
    Persist a new ThreatLog row from a detection-result dictionary.

    Designed to be called inside a BackgroundTask (HTTP endpoints) or an
    ``asyncio.create_task`` coroutine (WebSocket endpoint) so the caller's
    response is never delayed by the DB write.

    Args:
        db:       An open ``AsyncSession`` managed by the caller.
        log_data: Dict with keys ``module_type``, ``risk_level``, and
                  ``details_json``.  The ``id`` and ``timestamp`` fields
                  are populated automatically by the ORM column defaults.

    Returns:
        The newly committed ``ThreatLog`` instance (refreshed from DB).

    Raises:
        sqlalchemy.exc.SQLAlchemyError: on DB constraint violations or
        connectivity issues — callers should catch and log, not re-raise,
        since this runs in a background context.
    """
    log = ThreatLog(
        module_type=log_data["module_type"],
        risk_level=log_data["risk_level"],
        details_json=log_data["details_json"],
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    logger.debug(
        "ThreatLog created: id=%s module=%s risk=%s",
        log.id,
        log.module_type,
        log.risk_level,
    )
    return log


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

async def get_threat_logs(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 50,
    module_type: str | None = None,
) -> Sequence[ThreatLog]:
    """
    Return a paginated, recency-ordered list of ThreatLog entries.

    Args:
        db:          An open ``AsyncSession``.
        skip:        Number of rows to skip (offset-based pagination).
        limit:       Maximum rows to return (capped at 200 internally).
        module_type: Optional filter — ``'intent'`` | ``'audio'`` |
                     ``'document'``.  Pass ``None`` to return all modules.

    Returns:
        A sequence of ``ThreatLog`` ORM objects, newest first.
    """
    limit = min(limit, 200)  # hard cap — prevent runaway queries

    stmt = select(ThreatLog).order_by(desc(ThreatLog.timestamp))

    if module_type:
        stmt = stmt.where(ThreatLog.module_type == module_type)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def count_threat_logs(
    db: AsyncSession,
    *,
    module_type: str | None = None,
) -> int:
    """
    Return the total count of ThreatLog rows (optionally filtered by module).

    Used by the history endpoint to populate ``total`` in the paginated
    response so the frontend can render page indicators correctly.
    """
    stmt = select(func.count()).select_from(ThreatLog)
    if module_type:
        stmt = stmt.where(ThreatLog.module_type == module_type)
    result = await db.execute(stmt)
    return result.scalar_one()
