"""
Live Audio WebSocket endpoint for real-time deepfake voice detection.

Protocol
--------
1.  Client connects to ``ws://<host>/api/v1/live-audio/stream``.
2.  Client sends a UTF-8 JSON handshake frame:
        {"sample_rate": 16000, "channels": 1}
3.  Client streams binary frames containing raw float32 PCM samples
    (little-endian, interleaved if channels > 1).
4.  Server responds with a UTF-8 JSON frame after each analysis window:
        {
            "is_deepfake":       bool,
            "confidence_score":  float,  // 0-100
            "analysis_details":  str,
            "window_index":      int,
            "elapsed_ms":        float
        }
5.  Client sends a UTF-8 ``"STOP"`` frame (or closes the socket) to end
    the session.  Server replies with a final ``{"event": "session_end"}``
    frame before closing.

Design choices
--------------
- Samples are accumulated in a ``collections.deque`` rolling buffer.
- Analysis fires every ``_WINDOW_SAMPLES`` new samples (default 1 s at
  16 kHz) rather than after every frame, keeping the response cadence
  predictable without hammering the CPU on every tiny chunk.
- ``asyncio.get_running_loop().run_in_executor`` offloads the blocking
  librosa work so the FastAPI event loop is never stalled.
- The ``session_id`` in log messages helps correlate a single WebSocket
  conversation in production log aggregation (e.g. Loki/Cloud Logging).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections import deque

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.exc import SQLAlchemyError

from app.crud.crud_threat import create_threat_log
from app.db.database import AsyncSessionLocal
from app.services.audio_service import analyze_audio_chunk

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/live-audio",
    tags=["Live Audio — WebSocket"],
)


# ---------------------------------------------------------------------------
# Background DB logger for the WebSocket context
# ---------------------------------------------------------------------------

async def _fire_audio_log(log_data: dict) -> None:
    """
    Persist a deepfake detection event from the WebSocket streaming loop.

    WebSocket handlers cannot use FastAPI's BackgroundTasks mechanism, so
    we use ``asyncio.create_task`` to fire this coroutine as a non-blocking
    background task.  DB errors are caught and logged; the WebSocket session
    is never interrupted by a persistence failure.
    """
    try:
        async with AsyncSessionLocal() as db:
            await create_threat_log(db, log_data)
    except SQLAlchemyError as exc:
        logger.error("[live_audio] Failed to persist audio threat log: %s", exc)

# ---------------------------------------------------------------------------
# Streaming configuration
# ---------------------------------------------------------------------------

# Minimum PCM samples required for a meaningful analysis window.
# At 16 000 Hz this equals exactly 1 second of audio.
_DEFAULT_SAMPLE_RATE = 16_000
_WINDOW_SECONDS = 1.0

# Maximum accepted sample rate to prevent memory abuse.
_MAX_SAMPLE_RATE = 48_000

# Maximum number of raw bytes accepted in a single WebSocket frame (5 MB).
# float32 = 4 bytes/sample → 5 MB ≈ 1.25 M samples ≈ 78 s at 16 kHz.
_MAX_FRAME_BYTES = 5 * 1024 * 1024


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@router.websocket("/stream")
async def live_audio_stream(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time deepfake detection on streaming audio.

    See module docstring for the full client protocol.

    Args:
        websocket: FastAPI WebSocket connection object.
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]
    logger.info("[%s] WebSocket session opened.", session_id)

    # ------------------------------------------------------------------
    # Step 1 — Handshake: wait for the client to declare the sample rate.
    # ------------------------------------------------------------------
    sample_rate = _DEFAULT_SAMPLE_RATE
    try:
        handshake_raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        handshake = json.loads(handshake_raw)
        sample_rate = int(handshake.get("sample_rate", _DEFAULT_SAMPLE_RATE))

        if not (1 <= sample_rate <= _MAX_SAMPLE_RATE):
            await websocket.send_json(
                {"event": "error", "detail": f"sample_rate must be 1–{_MAX_SAMPLE_RATE} Hz."}
            )
            await websocket.close(code=1003)
            logger.warning("[%s] Rejected: invalid sample_rate=%s.", session_id, sample_rate)
            return

        await websocket.send_json(
            {
                "event": "handshake_ok",
                "sample_rate": sample_rate,
                "window_samples": int(_WINDOW_SECONDS * sample_rate),
                "session_id": session_id,
            }
        )
        logger.info("[%s] Handshake complete — sample_rate=%d Hz.", session_id, sample_rate)

    except asyncio.TimeoutError:
        await websocket.send_json({"event": "error", "detail": "Handshake timeout (10 s)."})
        await websocket.close(code=1001)
        return
    except (json.JSONDecodeError, ValueError) as exc:
        await websocket.send_json({"event": "error", "detail": f"Invalid handshake JSON: {exc}"})
        await websocket.close(code=1003)
        return

    # ------------------------------------------------------------------
    # Step 2 — Streaming loop
    # ------------------------------------------------------------------
    window_samples = int(_WINDOW_SECONDS * sample_rate)
    buffer: deque[np.ndarray] = deque()   # accumulates float32 chunks
    buffered_count = 0                    # total samples in buffer
    window_index = 0
    loop = asyncio.get_running_loop()

    try:
        while True:
            # Wait for the next frame from the client.
            message = await websocket.receive()

            # --- Control frame: STOP ----------------------------------------
            if message.get("type") == "websocket.receive":
                if message.get("text") is not None:
                    text_frame = message["text"].strip()
                    if text_frame.upper() == "STOP":
                        logger.info("[%s] Client sent STOP.", session_id)
                        break
                    # Ignore any other unexpected text frames gracefully.
                    continue

                # --- Binary frame: PCM data ---------------------------------
                raw_bytes: bytes = message.get("bytes", b"")

                if len(raw_bytes) == 0:
                    continue

                if len(raw_bytes) > _MAX_FRAME_BYTES:
                    await websocket.send_json(
                        {
                            "event": "error",
                            "detail": (
                                f"Frame too large ({len(raw_bytes)} bytes). "
                                f"Max is {_MAX_FRAME_BYTES} bytes."
                            ),
                        }
                    )
                    continue

                # Decode raw bytes as float32 PCM (little-endian).
                try:
                    chunk = np.frombuffer(raw_bytes, dtype="<f4").copy()
                except ValueError as exc:
                    await websocket.send_json(
                        {"event": "error", "detail": f"PCM decode error: {exc}"}
                    )
                    continue

                # Normalise peak to 1.0 to match analyze_voice_liveness.
                peak = np.max(np.abs(chunk))
                if peak > 0:
                    chunk = chunk / peak

                buffer.append(chunk)
                buffered_count += len(chunk)

                # ----------------------------------------------------------
                # Fire analysis each time we accumulate a full window.
                # ----------------------------------------------------------
                while buffered_count >= window_samples:
                    # Concatenate and slice exactly window_samples samples.
                    all_samples = np.concatenate(list(buffer))
                    window = all_samples[:window_samples]
                    remainder = all_samples[window_samples:]

                    # Reset buffer to the leftover samples.
                    buffer.clear()
                    if len(remainder) > 0:
                        buffer.append(remainder)
                    buffered_count = len(remainder)

                    # Offload blocking librosa work to a thread pool.
                    t0 = time.perf_counter()
                    result = await loop.run_in_executor(
                        None,                          # default ThreadPoolExecutor
                        analyze_audio_chunk,           # fn
                        window,                        # arg 1
                        sample_rate,                   # arg 2
                    )
                    elapsed_ms = (time.perf_counter() - t0) * 1_000

                    window_index += 1
                    payload = {
                        **result.model_dump(),
                        "window_index": window_index,
                        "elapsed_ms": round(elapsed_ms, 2),
                    }
                    await websocket.send_json(payload)
                    logger.debug(
                        "[%s] Window #%d — score=%.1f, elapsed=%.1f ms.",
                        session_id,
                        window_index,
                        result.confidence_score,
                        elapsed_ms,
                    )

                    # Persist threat log if this window flagged a deepfake.
                    if result.is_deepfake:
                        asyncio.create_task(
                            _fire_audio_log(
                                {
                                    "module_type": "audio",
                                    "risk_level": "DEEPFAKE_DETECTED",
                                    "details_json": {
                                        **result.model_dump(),
                                        "session_id": session_id,
                                        "window_index": window_index,
                                    },
                                }
                            )
                        )

    except WebSocketDisconnect:
        logger.info("[%s] Client disconnected.", session_id)
        return

    # ------------------------------------------------------------------
    # Step 3 — Clean close
    # ------------------------------------------------------------------
    await websocket.send_json(
        {"event": "session_end", "windows_analysed": window_index, "session_id": session_id}
    )
    await websocket.close(code=1000)
    logger.info("[%s] Session closed — %d windows analysed.", session_id, window_index)
