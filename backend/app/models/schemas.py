"""
Pydantic schemas for request/response validation.
These models ensure type safety and automatic API documentation.
"""

from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    """
    Request model for intent analysis endpoint.

    Accepts text content (call transcripts, SMS messages, etc.)
    for scam detection analysis.
    """
    transcript: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text content to analyze for scam indicators",
        examples=["Hello, this is the IRS. You owe $5000 in back taxes and must pay immediately or face arrest."]
    )


class IntentResponse(BaseModel):
    """
    Response model for intent analysis results.

    Returns comprehensive scam risk assessment with confidence scoring
    and detailed reasoning based on psychological pressure tactics.
    """
    is_scam: bool = Field(
        ...,
        description="Binary classification: True if scam detected, False if legitimate"
    )

    scam_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence score from 0 (definitely safe) to 100 (definitely scam)"
    )

    reason: str = Field(
        ...,
        description="Detailed explanation of the classification decision, including detected psychological tactics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "is_scam": True,
                "scam_score": 95,
                "reason": "High-pressure urgency tactics detected: mentions immediate payment, threatens legal action, impersonates authority figure (IRS). Classic social engineering pattern."
            }
        }


# ---------------------------------------------------------------------------
# Part 3 — Deepfake Voice Liveness Detection
# ---------------------------------------------------------------------------


class DeepfakeResponse(BaseModel):
    """
    Response model for deepfake voice liveness analysis.

    Returns a binary deepfake classification, a confidence score, and a
    human-readable summary of the audio features that drove the decision.
    """

    is_deepfake: bool = Field(
        ...,
        description="True if the audio is likely AI-generated / deepfake, False if it appears to be a genuine human voice"
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confidence percentage from 0.0 (certainly real) to 100.0 (certainly deepfake)"
    )

    analysis_details: str = Field(
        ...,
        description="Detailed breakdown of the acoustic features analysed and why the verdict was reached"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "is_deepfake": True,
                "confidence_score": 78.5,
                "analysis_details": (
                    "Spectral flatness is abnormally uniform (0.92) suggesting synthesised speech. "
                    "Pitch variability is very low (std=4.1 Hz) indicating monotone delivery typical of TTS. "
                    "Silence ratio is 0.03, unusually low for natural conversation."
                )
            }
        }


