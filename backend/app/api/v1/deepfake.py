"""
Deepfake Voice Liveness Detection endpoint.

Accepts an uploaded audio file, extracts acoustic features with librosa,
and returns a heuristic deepfake likelihood score.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.models.schemas import DeepfakeResponse
from app.services.audio_service import analyze_voice_liveness

# 10 MB upload limit — prevents accidental / malicious large uploads
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024

_ALLOWED_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/flac",
    "audio/ogg",
    "audio/webm",
    "application/octet-stream",  # some clients send this for audio
}

router = APIRouter(
    prefix="/analyze",
    tags=["Deepfake Detection"],
)


@router.post(
    "/audio",
    response_model=DeepfakeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse Audio for Deepfake Indicators",
    description="""
Upload an audio file (WAV, MP3, FLAC, OGG — max 10 MB) and receive a
deepfake liveness assessment.

**Detection focus:**
- Spectral flatness (uniform energy → synthetic)
- Pitch stability (monotone → TTS)
- Silence / pause ratio (no pauses → TTS)
- Zero-crossing rate smoothness (too smooth → neural vocoder)

**Returns:**
- Binary deepfake classification
- Confidence score (0-100)
- Detailed feature-level analysis
""",
)
async def analyze_audio(
    file: UploadFile = File(..., description="Audio file to analyse"),
) -> DeepfakeResponse:
    """
    Accept an audio upload, validate it, run acoustic analysis, and
    return a structured deepfake verdict.

    Raises:
        HTTPException 400 — empty file or unsupported content type
        HTTPException 413 — file exceeds 10 MB limit
        HTTPException 500 — internal analysis failure
    """

    # --- Content-type guard -------------------------------------------
    content_type = (file.content_type or "").lower()
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported audio type '{content_type}'. "
                f"Accepted: WAV, MP3, FLAC, OGG."
            ),
        )

    # --- Read bytes & enforce size limit ------------------------------
    try:
        file_bytes = await file.read()
    finally:
        # Always close the SpooledTemporaryFile to avoid memory leaks
        await file.close()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({len(file_bytes)} bytes) exceeds the 10 MB limit.",
        )

    # --- Run analysis -------------------------------------------------
    try:
        result = await analyze_voice_liveness(file_bytes)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio analysis failed: {str(exc)}",
        )

