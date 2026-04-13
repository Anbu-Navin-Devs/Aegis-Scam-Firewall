"""
Document Analysis API endpoint.

Accepts PDF, PNG, or JPEG uploads and uses Gemini Vision to detect
predatory, hidden, or unfair legal clauses inside the document.

Usage
-----
POST /api/v1/document/scan
  • Body: multipart/form-data  — field name ``file``
  • Accepted MIME types: application/pdf, image/png, image/jpeg

Response: ``DocumentAnalysisResponse`` JSON
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, status
from sqlalchemy.exc import SQLAlchemyError

from app.crud.crud_threat import create_threat_log
from app.db.database import AsyncSessionLocal
from app.models.schemas import DocumentAnalysisResponse
from app.services.gemini_service import analyze_document

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# 20 MB — large enough for a multi-page contract scan, small enough to stay
# within Gemini's inline data limit without Base64 overhead issues.
_MAX_UPLOAD_BYTES = 20 * 1024 * 1024

# Maps accepted content-type headers to the MIME type string expected by the
# Gemini SDK.  The SDK requires the exact RFC 2046 MIME type.
_ACCEPTED_MIME_TYPES: dict[str, str] = {
    "application/pdf":    "application/pdf",
    "image/png":          "image/png",
    "image/jpeg":         "image/jpeg",
    "image/jpg":          "image/jpeg",   # some clients send image/jpg
    # Catch-all for clients that send a generic binary type for a known format.
    # We rely on the file extension check later to disambiguate.
    "application/octet-stream": None,     # resolved from filename extension
}

_EXT_TO_MIME: dict[str, str] = {
    ".pdf":  "application/pdf",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
}

router = APIRouter(
    prefix="/document",
    tags=["Document Analysis"],
)


# ---------------------------------------------------------------------------
# Background helper — fires after HTTP response is sent
# ---------------------------------------------------------------------------

async def _persist_document_log(log_data: dict) -> None:
    """
    Write a document-scan ThreatLog entry asynchronously.

    Called as a FastAPI BackgroundTask so the multipart upload response
    is returned to the client before the database round-trip completes.
    DB errors are logged and swallowed — the client has already received
    its verdict and must not be affected by persistence failures.
    """
    try:
        async with AsyncSessionLocal() as db:
            await create_threat_log(db, log_data)
    except Exception as exc:  # broad catch: SQLAlchemy or connectivity
        logger.error("Failed to persist document threat log: %s", exc)


@router.post(
    "/scan",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Scan a Document for Predatory Clauses",
    description="""
Upload a **PDF, PNG, or JPEG** document (max 20 MB) to detect predatory,
hidden, or legally unfair clauses using Gemini Vision AI.

**Detection focus:**
- Hidden auto-renewal or cancellation penalties
- Asymmetric liability clauses favouring only one party
- Buried arbitration / class-action waiver terms
- Vague data sharing or data sale permissions
- Unreasonable forfeiture, liquidated damages, or indemnity clauses
- Deceptive payment terms or price-escalation mechanisms

**Returns:**
- `risk_level` — `SAFE`, `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`
- `flagged_clauses` — list of exact or paraphrased problematic clauses
- `summary` — plain-English executive summary of the findings
""",
)
async def scan_document(
    file: UploadFile = File(..., description="PDF, PNG, or JPEG document to analyse"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> DocumentAnalysisResponse:
    """
    Validate the upload, read its bytes, and forward to the Gemini
    document analysis service.

    Raises:
        HTTPException 400 — empty file, unsupported content type.
        HTTPException 413 — file exceeds the 20 MB size limit.
        HTTPException 500 — Gemini service call failed.
    """

    # -- MIME-type resolution ------------------------------------------------
    content_type = (file.content_type or "").lower().split(";")[0].strip()
    mime_type: str | None = _ACCEPTED_MIME_TYPES.get(content_type)

    # For application/octet-stream, try to resolve from the filename extension.
    if mime_type is None and content_type == "application/octet-stream":
        filename = (file.filename or "").lower()
        for ext, resolved in _EXT_TO_MIME.items():
            if filename.endswith(ext):
                mime_type = resolved
                break

    if mime_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type '{content_type}'. "
                "Accepted formats: PDF, PNG, JPEG."
            ),
        )

    # -- Read bytes & enforce size limit -------------------------------------
    try:
        file_bytes = await file.read()
    finally:
        await file.close()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File size ({len(file_bytes):,} bytes) exceeds the 20 MB limit."
            ),
        )

    # -- Gemini analysis -----------------------------------------------------
    try:
        result = await analyze_document(file_bytes, mime_type)

        # Queue persistence — fires after the response is flushed to client.
        background_tasks.add_task(
            _persist_document_log,
            {
                "module_type": "document",
                "risk_level": result.risk_level.value,
                "details_json": result.model_dump(),
            },
        )

        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(exc)}",
        )
