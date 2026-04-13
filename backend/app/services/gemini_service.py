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


# ---------------------------------------------------------------------------
# Part 4 — Document / Predatory Clause Detection
# ---------------------------------------------------------------------------

# Gemini 1.5 Flash supports inline vision (PDF + image) up to 20 MB.
# We use Flash rather than Pro to minimise latency for document uploads;
# swap to "gemini-1.5-pro" here if higher recall is needed on complex contracts.
_document_model = genai.GenerativeModel("gemini-1.5-flash")

DOCUMENT_ANALYSIS_PROMPT = """\
You are an expert legal analyst and consumer-protection AI specialising in
detecting predatory, hidden, and unfair clauses inside contracts, terms of
service, loan agreements, insurance policies, and similar documents.

Your mission: Carefully examine EVERY page of the supplied document.
Identify clauses that are harmful, deceptive, one-sided, or designed to
disadvantage the signing party.

**Categories of predatory clauses to flag:**
1. Hidden auto-renewal or price-escalation mechanisms
2. Binding mandatory arbitration or class-action waivers
3. Asymmetric liability (company not liable, consumer fully liable)
4. Vague or broad data-sharing / data-sale permissions
5. Unreasonable forfeiture, liquidated damages, or early-termination fees
6. Unilateral right to modify terms without notice
7. Clauses that waive statutory consumer rights
8. Unconscionable penalty or interest-rate provisions
9. Jurisdiction clauses designed to make dispute resolution impractical
10. Fine-print terms that contradict headline marketing claims

**RESPONSE FORMAT — strictly valid JSON, no markdown, no commentary:**
{
  "risk_level": "<SAFE|LOW|MEDIUM|HIGH|CRITICAL>",
  "flagged_clauses": [
    "Exact quoted or faithfully paraphrased clause with section reference"
  ],
  "summary": "Plain-English executive summary (3-5 sentences) explaining the verdict and the most critical findings."
}

**Risk-level definitions:**
- SAFE     → No problematic clauses; document appears fair and transparent.
- LOW      → 1-2 minor concerns unlikely to cause significant harm.
- MEDIUM   → 3-5 questionable clauses that warrant careful reading.
- HIGH     → Multiple predatory clauses; legal review recommended before signing.
- CRITICAL → Extremely one-sided or deceptive; do NOT sign without specialist counsel.

Return ONLY the JSON object. Do not include any explanation outside the JSON.\
"""


async def analyze_document(
    file_bytes: bytes,
    mime_type: str,
) -> "DocumentAnalysisResponse":
    """
    Analyse a document (PDF, PNG, or JPEG) for predatory legal clauses.

    Sends the raw file bytes to Gemini 1.5 Flash as an inline vision blob
    so the model can read every page of the document directly.  The model
    is instructed to return strict JSON matching ``DocumentAnalysisResponse``.

    Args:
        file_bytes: Raw bytes of the uploaded document.
        mime_type:  RFC 2046 MIME type string (e.g. ``"application/pdf"``).

    Returns:
        DocumentAnalysisResponse with ``risk_level``, ``flagged_clauses``,
        and ``summary``.

    Raises:
        ValueError: If the Gemini response cannot be parsed as valid JSON.
        Exception:  If the Gemini API call itself fails.
    """
    # Import here to avoid a circular import at module initialisation time.
    from app.models.schemas import DocumentAnalysisResponse, RiskLevel

    # Build the multipart request: system prompt text + raw file blob.
    document_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": file_bytes,
        }
    }

    try:
        response = _document_model.generate_content(
            [DOCUMENT_ANALYSIS_PROMPT, document_part]
        )

        response_text = response.text.strip()

        # Strip markdown code fences that Gemini sometimes adds.
        if response_text.startswith("```json"):
            response_text = response_text.removeprefix("```json").removesuffix("```").strip()
        elif response_text.startswith("```"):
            response_text = response_text.removeprefix("```").removesuffix("```").strip()

        data = json.loads(response_text)

        return DocumentAnalysisResponse(
            risk_level=RiskLevel(data["risk_level"].upper()),
            flagged_clauses=data.get("flagged_clauses", []),
            summary=data["summary"],
        )

    except json.JSONDecodeError as exc:
        # Gemini returned non-JSON — surface a safe fallback so the endpoint
        # does not 500 on a format glitch; the client gets a MEDIUM warning.
        raw_preview = response.text[:300] if "response" in dir() else "unavailable"
        return DocumentAnalysisResponse(
            risk_level=RiskLevel.MEDIUM,
            flagged_clauses=[],
            summary=(
                f"Document analysis completed but the AI returned an unparseable response. "
                f"Manual review is recommended. (parse error: {exc}; preview: {raw_preview})"
            ),
        )

    except Exception as exc:
        # Re-raise so the router can return a clean 500 with context.
        raise RuntimeError(f"Gemini document analysis error: {exc}") from exc
