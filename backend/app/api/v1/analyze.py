"""
Intent Analysis API Endpoints.

Provides cognitive scam detection through AI-powered analysis
of text transcripts using psychological pressure tactic identification.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import IntentRequest, IntentResponse
from app.services.gemini_service import analyze_transcript_intent

# Create router with consistent tagging for API documentation
router = APIRouter(
    prefix="/analyze",
    tags=["Intent Analysis"]
)


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
async def analyze_intent(request: IntentRequest) -> IntentResponse:
    """
    Analyze text content for scam indicators using Gemini AI.

    This endpoint leverages Google's Gemini 1.5 Flash model to perform
    sophisticated intent analysis, identifying psychological manipulation
    tactics commonly employed in social engineering attacks.

    Args:
        request: IntentRequest containing the text transcript to analyze

    Returns:
        IntentResponse: Comprehensive analysis including scam classification,
                       confidence score, and detailed reasoning

    Raises:
        HTTPException: 400 if transcript is empty or invalid
        HTTPException: 500 if AI analysis service fails
    """
    # Validate input
    if not request.transcript or not request.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty"
        )

    try:
        # Call the Gemini service to perform intent analysis
        result = await analyze_transcript_intent(request.transcript)
        return result

    except Exception as e:
        # Log the error in production, return generic message to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent analysis failed: {str(e)}"
        )

