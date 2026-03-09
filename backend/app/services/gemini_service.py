"""
Google Gemini AI service for cognitive intent analysis.

This module uses Gemini 1.5 Flash to detect scam patterns through
psychological pressure tactic analysis (urgency, authority, fear).
"""

import json
import google.generativeai as genai
from app.core.config import settings
from app.models.schemas import IntentResponse

# Initialize Gemini client with API key from environment
genai.configure(api_key=settings.GEMINI_API_KEY)

# Configure the Gemini 1.5 Flash model for optimal cost/performance
model = genai.GenerativeModel('gemini-1.5-flash')

# System prompt that defines AI behavior as a scam detection firewall
SCAM_DETECTION_PROMPT = """You are an expert Scam Detection Firewall trained to analyze communications for social engineering and fraud indicators.

Your primary mission: Evaluate text (call transcripts, SMS messages, emails) for psychological manipulation tactics commonly used by scammers.

**Key Red Flags to Detect:**
1. **Urgency Pressure** - "Act now!", "Limited time!", "Immediate action required"
2. **Authority Impersonation** - Claims to be from government, banks, tech support, law enforcement
3. **Fear Tactics** - Threats of arrest, account suspension, legal action, data breach
4. **Financial Demands** - Requests for gift cards, wire transfers, cryptocurrency, prepaid cards
5. **Information Harvesting** - Asks for passwords, SSN, credit card details, OTP codes
6. **Too-Good-To-Be-True Offers** - Lottery wins, inheritance, free money, guaranteed returns
7. **Emotional Manipulation** - Exploits fear, greed, compassion, curiosity

**Analysis Format:**
Analyze the provided text and respond ONLY with valid JSON in this exact structure:
{
  "is_scam": true or false,
  "scam_score": integer from 0-100,
  "reason": "Detailed explanation of detected tactics"
}

**Scoring Guidelines:**
- 0-20: Clearly legitimate communication
- 21-40: Low risk, minor suspicious elements
- 41-60: Moderate risk, several red flags present
- 61-80: High risk, multiple manipulation tactics detected
- 81-100: Extreme risk, obvious scam attempt

Be precise. Explain which specific psychological pressure tactics you detected and why they indicate scam behavior."""


async def analyze_transcript_intent(transcript: str) -> IntentResponse:
    """
    Analyze text content for scam intent using Gemini AI.

    This function sends the transcript to Gemini 1.5 Flash with a specialized
    prompt that instructs the AI to detect psychological manipulation tactics
    commonly used in social engineering attacks.

    Args:
        transcript: The text content to analyze (call transcript, message, etc.)

    Returns:
        IntentResponse: Structured analysis with scam classification, confidence score,
                       and detailed reasoning about detected tactics.

    Raises:
        ValueError: If the AI response cannot be parsed as valid JSON
        Exception: If the Gemini API call fails
    """
    try:
        # Construct the full prompt with system instructions + user content
        full_prompt = f"{SCAM_DETECTION_PROMPT}\n\n**TEXT TO ANALYZE:**\n{transcript}"

        # Call Gemini API (synchronously for now - FastAPI will handle async wrapping)
        response = model.generate_content(full_prompt)

        # Extract JSON from the response text
        response_text = response.text.strip()

        # Handle markdown code blocks if Gemini wraps response in ```json
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        # Parse the JSON response
        analysis_data = json.loads(response_text)

        # Validate and return as Pydantic model
        return IntentResponse(
            is_scam=analysis_data["is_scam"],
            scam_score=analysis_data["scam_score"],
            reason=analysis_data["reason"]
        )

    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails - return high-risk warning
        return IntentResponse(
            is_scam=True,
            scam_score=50,
            reason=f"AI analysis failed to parse properly. Raw response: {response.text[:200]}. Error: {str(e)}"
        )
    except Exception as e:
        # Generic error handler - return error information
        return IntentResponse(
            is_scam=False,
            scam_score=0,
            reason=f"Analysis engine error: {str(e)}"
        )

