"""
Intent Analysis API Endpoints.

Provides cognitive scam detection through AI-powered analysis
of text transcripts using psychological pressure tactic identification.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.crud.crud_threat import create_threat_log
from app.db.database import AsyncSessionLocal
from app.models.schemas import IntentRequest, IntentResponse
from app.services.nvidia_service import analyze_transcript_intent

logger = logging.getLogger(__name__)

# Create router with consistent tagging for API documentation
router = APIRouter(
    prefix="/analyze",
    tags=["Intent Analysis"]
)


# ---------------------------------------------------------------------------
# Background helper — runs after the HTTP response is sent
# ---------------------------------------------------------------------------

async def _persist_intent_log(log_data: dict) -> None:
    """
    Write an intent-analysis ThreatLog row asynchronously.

    Runs as a FastAPI BackgroundTask so the HTTP response is returned to
    the Flutter client before the DB round-trip completes.  Any DB error
    is logged but NOT re-raised (the client has already received its reply).
    """
    try:
        async with AsyncSessionLocal() as db:
            await create_threat_log(db, log_data)
    except SQLAlchemyError as exc:
        logger.error("Failed to persist intent threat log: %s", exc)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/intent",
    response_model=IntentResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Text for Scam Intent",
    description="""
    Performs cognitive analysis of text content (call transcripts, SMS messages, emails)
    to detect social engineering and scam patterns.

    **Detection Focus:**
    - Urgency and pressure tactics
    - Authority impersonation
    - Fear-based manipulation
    - Financial fraud indicators
    - Information harvesting attempts

    **Returns:**
    - Binary scam classification (is_scam: true/false)
    - Confidence score (0-100)
    - Detailed reasoning explaining detected psychological tactics
    """
)
async def analyze_intent(
    request: IntentRequest,
    background_tasks: BackgroundTasks,
) -> IntentResponse:
    """
    Analyze text content for scam indicators using NVIDIA NIM (Llama 3.3).

    After returning the AI verdict to the caller, a BackgroundTask
    persists the result to the ``threat_logs`` PostgreSQL table without
    blocking the response.

    Args:
        request:          IntentRequest containing the text transcript to analyze.
        background_tasks: FastAPI BackgroundTasks injected by the framework.

    Returns:
        IntentResponse: Comprehensive analysis including scam classification,
                       confidence score, and detailed reasoning.

    Raises:
        HTTPException: 400 if transcript is empty or invalid.
        HTTPException: 500 if AI analysis service fails.
    """
    # Validate input
    if not request.transcript or not request.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty"
        )

    try:
        # Call the NVIDIA NIM service to perform intent analysis
        result = await analyze_transcript_intent(request.transcript)

        # Queue DB persistence — fires after response is sent to client
        risk_label = "SCAM_DETECTED" if result.is_scam else "CLEAN"
        background_tasks.add_task(
            _persist_intent_log,
            {
                "module_type": "intent",
                "risk_level": risk_label,
                "details_json": result.model_dump(),
            },
        )

        return result

    except Exception as e:
        # Log the error in production, return generic message to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent analysis failed: {str(e)}"
        )

