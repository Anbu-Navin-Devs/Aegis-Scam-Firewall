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

