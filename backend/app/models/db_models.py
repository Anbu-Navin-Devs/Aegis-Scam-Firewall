"""
SQLAlchemy ORM models for the Aegis backend.

All models inherit from ``Base`` defined in ``app.db.database`` so they are
automatically picked up by ``Base.metadata.create_all`` when the application
starts.

ThreatLog
---------
Stores every detected threat event produced by any of the three analysis
modules (intent, audio, document).  The ``details_json`` column stores the
full Pydantic response payload as JSONB so downstream queries can filter on
specific fields without schema migrations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ThreatLog(Base):
    """
    Persisted record of a single threat detection event.

    Each row is written by one of the three analysis modules immediately
    after the AI verdict is produced, using either a BackgroundTask (for
    HTTP endpoints) or an ``asyncio.create_task`` fire-and-forget (for the
    WebSocket live-audio endpoint).

    Columns
    -------
    id           : UUID primary key, generated in Python via uuid4() for
                   portability across DB flavours.
    timestamp    : UTC datetime of the event; indexed for fast dashboard
                   queries ordered by recency.
    module_type  : Which Aegis module produced the log:
                   ``'intent'`` | ``'audio'`` | ``'document'``
    risk_level   : Human-readable risk label from the module verdict,
                   e.g. ``'HIGH'``, ``'SAFE'``, ``'CRITICAL'``, or the
                   boolean-based ``'SCAM_DETECTED'`` / ``'CLEAN'`` used by
                   the intent/audio modules.
    details_json : Full Pydantic response payload serialised to JSONB.
                   Supports ad-hoc PostgreSQL JSON-path queries for
                   analytics without requiring column migrations.
    """

    __tablename__ = "threat_logs"

    # Primary key ────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for this threat log entry.",
    )

    # Timestamp ──────────────────────────────────────────────────────────────
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        doc="UTC datetime when the threat was detected.",
    )

    # Module that produced the log ────────────────────────────────────────────
    module_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        doc="Analysis module: 'intent' | 'audio' | 'document'.",
    )

    # Risk label ─────────────────────────────────────────────────────────────
    risk_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Risk verdict string (e.g. 'HIGH', 'SAFE', 'SCAM_DETECTED').",
    )

    # Full AI response payload ─────────────────────────────────────────────
    details_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        doc="Complete serialised Pydantic response from the detection module.",
    )

    def __repr__(self) -> str:
        return (
            f"<ThreatLog id={self.id} module={self.module_type!r} "
            f"risk={self.risk_level!r} ts={self.timestamp.isoformat()}>"
        )
