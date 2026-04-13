"""
Threat History API — dashboard log retrieval.

Exposes a paginated read endpoint so the Flutter frontend dashboard can
display a timeline of all past detection events from every module.

Endpoints
---------
GET /api/v1/history/logs
    Query params:
      skip        (int, default 0)   — offset for pagination
      limit       (int, default 20)  — rows per page, max 200
      module_type (str, optional)    — filter by 'intent'|'audio'|'document'

Response: ``ThreatLogPage`` — contains ``total``, ``skip``, ``limit``,
and a ``logs`` list of ``ThreatLogRead`` objects.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Sequence

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_threat import count_threat_logs, get_threat_logs
from app.db.database import get_db

router = APIRouter(
    prefix="/history",
    tags=["Threat History"],
)


# ---------------------------------------------------------------------------
# Response schemas (local — no circular import with models/schemas.py)
# ---------------------------------------------------------------------------


class ThreatLogRead(BaseModel):
    """
    Read-only representation of a single persisted ThreatLog row.

    ``details_json`` carries the full original AI verdict so the frontend
    can render module-specific fields (scam_score, flagged_clauses, etc.)
    without a separate lookup.
    """

    id: uuid.UUID = Field(..., description="Unique row identifier.")
    timestamp: datetime = Field(..., description="UTC datetime of detection.")
    module_type: str = Field(
        ..., description="Analysis module: 'intent' | 'audio' | 'document'."
    )
    risk_level: str = Field(..., description="Risk verdict string from the module.")
    details_json: dict = Field(..., description="Full AI response payload.")

    model_config = {"from_attributes": True}  # allows ORM → Pydantic conversion


class ThreatLogPage(BaseModel):
    """Paginated response envelope for the /logs endpoint."""

    total: int = Field(..., description="Total matching rows in the database.")
    skip: int = Field(..., description="Current offset (rows skipped).")
    limit: int = Field(..., description="Maximum rows per page.")
    logs: Sequence[ThreatLogRead] = Field(
        ..., description="List of ThreatLog entries, newest first."
    )

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/logs",
    response_model=ThreatLogPage,
    status_code=status.HTTP_200_OK,
    summary="List Threat Detection Logs",
    description="""
Return a **paginated, recency-ordered** list of all threat events detected
by the Aegis backend.  Use the optional ``module_type`` filter to drill
into a specific analysis module.

**Query parameters:**
- `skip`        — rows to skip (default 0)
- `limit`       — rows per page, max 200 (default 20)
- `module_type` — filter: `intent` | `audio` | `document`

**Use case:** powers the Flutter threat-history dashboard.
""",
)
async def list_threat_logs(
    skip: int = Query(default=0, ge=0, description="Rows to skip (offset)."),
    limit: int = Query(default=20, ge=1, le=200, description="Rows per page (max 200)."),
    module_type: Optional[str] = Query(
        default=None,
        description="Filter by module: 'intent' | 'audio' | 'document'.",
    ),
    db: AsyncSession = Depends(get_db),
) -> ThreatLogPage:
    """
    Fetch paginated ThreatLog rows from PostgreSQL.

    Both the list query and the count query run concurrently via
    ``asyncio.gather`` to minimise round-trip latency on large datasets.

    Args:
        skip:        Pagination offset.
        limit:       Page size (capped at 200 in the CRUD layer).
        module_type: Optional module filter string.
        db:          Injected async database session.

    Returns:
        ``ThreatLogPage`` with total count, pagination metadata, and logs.
    """
    import asyncio

    logs, total = await asyncio.gather(
        get_threat_logs(db, skip=skip, limit=limit, module_type=module_type),
        count_threat_logs(db, module_type=module_type),
    )

    return ThreatLogPage(
        total=total,
        skip=skip,
        limit=limit,
        logs=logs,  # type: ignore[arg-type]
    )
