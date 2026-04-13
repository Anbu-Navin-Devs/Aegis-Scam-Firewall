"""
Pydantic schemas for request/response validation.
These models ensure type safety and automatic API documentation.
"""

from enum import Enum
from typing import List

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


# ---------------------------------------------------------------------------
# Part 4 — Document / Predatory Clause Detection
# ---------------------------------------------------------------------------


class RiskLevel(str, Enum):
    """
    Categorical risk rating assigned to a scanned document.

    Inheriting from ``str`` makes the enum JSON-serialisable as a plain
    string without any extra Pydantic configuration.
    """
    SAFE     = "SAFE"      # No problematic clauses found
    LOW      = "LOW"       # Minor concerns, unlikely to cause harm
    MEDIUM   = "MEDIUM"    # Several questionable clauses warrant review
    HIGH     = "HIGH"      # Multiple predatory clauses detected
    CRITICAL = "CRITICAL"  # Extremely unfair; do not sign without counsel


class DocumentAnalysisResponse(BaseModel):
    """
    Response model for document predatory-clause detection.

    Returned by ``POST /api/v1/document/scan`` after Gemini Vision
    analyses the uploaded PDF, PNG, or JPEG for hidden or unfair legal
    language.
    """

    risk_level: RiskLevel = Field(
        ...,
        description=(
            "Overall risk category of the document: "
            "SAFE | LOW | MEDIUM | HIGH | CRITICAL"
        ),
    )

    flagged_clauses: List[str] = Field(
        ...,
        description=(
            "List of exact or paraphrased clauses identified as predatory, "
            "hidden, or legally unfair. Empty list when risk_level is SAFE."
        ),
    )

    summary: str = Field(
        ...,
        description=(
            "Plain-English executive summary of the analysis, explaining "
            "the overall risk verdict and the most critical findings."
        ),
    )

    class Config:
        json_schema_extra = {
            "example": {
                "risk_level": "HIGH",
                "flagged_clauses": [
                    "Section 4.2: Auto-renewal clause hidden in fine print — subscription renews annually at full price unless cancelled 90 days in advance.",
                    "Section 7.1: Mandatory binding arbitration waiver prevents any class-action lawsuit against the company.",
                    "Section 9.3: Company retains the right to sell user data to 'affiliated third parties' without individual consent.",
                    "Section 12: Liquidated damages clause charges 150% of remaining contract value upon early termination.",
                ],
                "summary": (
                    "This contract contains four HIGH-risk clauses. The auto-renewal and liquidated "
                    "damages terms create significant financial liability, while the arbitration waiver "
                    "removes your right to collective legal action. The data-sharing clause is vague "
                    "and grants broad third-party access rights. Legal review is strongly recommended "
                    "before signing."
                ),
            }
        }
