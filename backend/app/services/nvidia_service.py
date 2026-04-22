"""
NVIDIA AI service for cognitive intent analysis and document scanning.

This module replaces Gemini with NVIDIA's NIM endpoints:
- meta/llama-3.3-70b-instruct for text intent analysis.
- meta/llama-3.2-11b-vision-instruct for document analysis.
"""

import json
import base64
import fitz  # PyMuPDF
from openai import AsyncOpenAI
from app.models.schemas import IntentResponse
from app.core.config import settings

# Using the NVIDIA API key from settings
NVIDIA_API_KEY = settings.NVIDIA_API_KEY
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Initialize the AsyncOpenAI client pointing to NVIDIA NIM
client = AsyncOpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY
)

TEXT_MODEL = "meta/llama-3.3-70b-instruct"
VISION_MODEL = "meta/llama-3.2-11b-vision-instruct"

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
    Analyze text content for scam intent using Llama 3.3 70B via NVIDIA NIM.
    """
    try:
        full_prompt = f"{SCAM_DETECTION_PROMPT}\n\n**TEXT TO ANALYZE:**\n{transcript}"

        completion = await client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=False
        )

        response_text = completion.choices[0].message.content.strip()

        # Handle markdown code blocks if the model wraps response in ```json
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        analysis_data = json.loads(response_text)

        return IntentResponse(
            is_scam=analysis_data["is_scam"],
            scam_score=analysis_data["scam_score"],
            reason=analysis_data["reason"]
        )

    except json.JSONDecodeError as e:
        return IntentResponse(
            is_scam=True,
            scam_score=50,
            reason=f"AI analysis failed to parse properly. Error: {str(e)}"
        )
    except Exception as e:
        return IntentResponse(
            is_scam=False,
            scam_score=0,
            reason=f"Analysis engine error: {str(e)}"
        )


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

**RESPONSE FORMAT - strictly valid JSON, no markdown, no commentary:**
{
  "risk_level": "<SAFE|LOW|MEDIUM|HIGH|CRITICAL>",
  "flagged_clauses": [
    "Exact quoted or faithfully paraphrased clause with section reference"
  ],
  "summary": "Plain-English executive summary (3-5 sentences) explaining the verdict and the most critical findings."
}

**Risk-level definitions:**
- SAFE     -> No problematic clauses; document appears fair and transparent.
- LOW      -> 1-2 minor concerns unlikely to cause significant harm.
- MEDIUM   -> 3-5 questionable clauses that warrant careful reading.
- HIGH     -> Multiple predatory clauses; legal review recommended before signing.
- CRITICAL -> Extremely one-sided or deceptive; do NOT sign without specialist counsel.

Return ONLY the JSON object. Do not include any explanation outside the JSON.\
"""


async def analyze_document(
    file_bytes: bytes,
    mime_type: str,
) -> "DocumentAnalysisResponse":
    """
    Analyse a document (PDF, PNG, or JPEG) for predatory legal clauses using Llama Vision.
    If the input is a PDF, it is automatically converted into images first.
    """
    from app.models.schemas import DocumentAnalysisResponse, RiskLevel

    image_parts = []

    # Handle PDF conversion
    if mime_type == "application/pdf":
        try:
            # Open the PDF from memory
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            
            # Limit to the first 5 pages to keep the payload reasonable
            # Legal documents can be long, but predatory clauses are often in the first few pages
            # or the 'General Terms' at the beginning/end.
            max_pages = min(len(doc), 5)
            
            for page_num in range(max_pages):
                page = doc.load_page(page_num)
                # Render page to an image (2.0 scale for better OCR quality)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                b64_img = base64.b64encode(img_data).decode('utf-8')
                image_parts.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/png;base64,{b64_img}"}
                })
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF: {str(e)}")
    else:
        # Standard image (PNG/JPEG)
        b64_img = base64.b64encode(file_bytes).decode('utf-8')
        image_parts.append({
            "type": "image_url", 
            "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}
        })

    if not image_parts:
        raise ValueError("No images found to analyze.")

    # Prepare the message content list
    content = [{"type": "text", "text": DOCUMENT_ANALYSIS_PROMPT}] + image_parts

    try:
        completion = await client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": content
            }],
            max_tokens=1024,
            temperature=0.2,
            stream=False
        )

        response_text = completion.choices[0].message.content.strip()
        
        # Robust JSON extraction
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # If it's still not valid JSON, try to extract fields manually or return a safe error
            return DocumentAnalysisResponse(
                risk_level=RiskLevel.MEDIUM,
                flagged_clauses=[],
                summary=(
                    f"The AI analyzed the document but returned a non-standard response. "
                    f"Raw response: {response_text[:500]}"
                ),
            )

        return DocumentAnalysisResponse(
            risk_level=RiskLevel(data.get("risk_level", "MEDIUM").upper()),
            flagged_clauses=data.get("flagged_clauses", []),
            summary=data.get("summary", "Analysis completed but summary was missing."),
        )

    except json.JSONDecodeError as exc:
        return DocumentAnalysisResponse(
            risk_level=RiskLevel.MEDIUM,
            flagged_clauses=[],
            summary=(
                f"Document analysis completed but the AI returned an unparseable response. "
                f"Manual review is recommended. (parse error: {exc})"
            ),
        )
    except Exception as exc:
        raise RuntimeError(f"NVIDIA document analysis error: {exc}") from exc
