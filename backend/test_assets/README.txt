# Aegis Test Assets
# ══════════════════════════════════════════════════════════════
#
# This folder contains ready-to-use test payloads for every
# Aegis backend endpoint. Use these to verify the API is working
# correctly before wiring up the Flutter UI.
#
# ──────────────────────────────────────────────────────────────
# FILE INVENTORY
# ──────────────────────────────────────────────────────────────
#
#  sample_intent.json         → POST /api/v1/analyze/intent
#  sample_scam_contract.txt   → POST /api/v1/document/scan
#  README.txt                 → This file (WebSocket guide inside)
#
# ──────────────────────────────────────────────────────────────
# 1. INTENT ANALYSIS  (sample_intent.json)
# ──────────────────────────────────────────────────────────────
#
#  In Postman / Bruno:
#    Method : POST
#    URL    : http://localhost:8000/api/v1/analyze/intent
#    Headers: Content-Type: application/json
#    Body   : (paste contents of sample_intent.json)
#
#  Expected response:
#    { "is_scam": true, "scam_score": > 85, "reason": "..." }
#
# ──────────────────────────────────────────────────────────────
# 2. DOCUMENT SCANNING  (sample_scam_contract.txt)
# ──────────────────────────────────────────────────────────────
#
#  The Gemini Vision endpoint accepts PDF, PNG, and JPEG.
#  To test with the .txt file provided:
#    a) Open the .txt in a browser (or Word/LibreOffice)
#    b) Save/export as PDF → name it sample_scam_contract.pdf
#    c) Upload via Postman → Body → form-data:
#         key  : file   (type: File)
#         value: select sample_scam_contract.pdf
#    URL: http://localhost:8000/api/v1/document/scan
#
#  Expected response:
#    { "risk_level": "CRITICAL", "flagged_clauses": [...], "summary": "..." }
#
# ──────────────────────────────────────────────────────────────
# 3. LIVE AUDIO WebSocket  (/api/v1/live-audio/stream)
# ──────────────────────────────────────────────────────────────
#
#  The WebSocket endpoint expects binary float32 PCM audio frames
#  (little-endian, mono). Here is how to convert a standard WAV
#  file into the required format using Python:
#
#  ┌─────────────────────────────────────────────────────────┐
#  │  STEP 1 — Install dependencies (one-time)               │
#  │                                                         │
#  │  pip install soundfile numpy websockets                 │
#  └─────────────────────────────────────────────────────────┘
#
#  ┌─────────────────────────────────────────────────────────┐
#  │  STEP 2 — Convert & stream (save as ws_test.py)         │
#  │                                                         │
#  │  import asyncio, json, numpy as np, soundfile as sf     │
#  │  import websockets                                       │
#  │                                                         │
#  │  WAV_FILE = "your_audio.wav"    # any mono/stereo WAV   │
#  │  TARGET_SR = 16000              # 16 kHz recommended    │
#  │  WS_URL = "ws://localhost:8000/api/v1/live-audio/stream"│
#  │                                                         │
#  │  async def stream():                                     │
#  │      data, sr = sf.read(WAV_FILE, dtype="float32")      │
#  │      if data.ndim > 1:                                   │
#  │          data = data.mean(axis=1)     # mono mix        │
#  │                                                         │
#  │      async with websockets.connect(WS_URL) as ws:       │
#  │          # Handshake                                     │
#  │          await ws.send(json.dumps({"sample_rate": sr})) │
#  │          print(await ws.recv())  # handshake_ok         │
#  │                                                         │
#  │          # Stream in 1-second chunks                     │
#  │          chunk_size = sr                                 │
#  │          for i in range(0, len(data), chunk_size):      │
#  │              chunk = data[i:i+chunk_size]               │
#  │              await ws.send(chunk.tobytes())              │
#  │              try:                                        │
#  │                  msg = await asyncio.wait_for(          │
#  │                      ws.recv(), timeout=2.0)            │
#  │                  print(json.loads(msg))                 │
#  │              except asyncio.TimeoutError:               │
#  │                  pass   # window not full yet            │
#  │                                                         │
#  │          await ws.send("STOP")                          │
#  │          print(await ws.recv())  # session_end          │
#  │                                                         │
#  │  asyncio.run(stream())                                   │
#  └─────────────────────────────────────────────────────────┘
#
#  WHAT IS float32 PCM?
#    - Each audio sample is a 32-bit floating point number
#    - Values are normalised to the range [-1.0, +1.0]
#    - Little-endian byte order (standard on x86/ARM)
#    - 4 bytes per sample → 1 second at 16 kHz = 64,000 bytes
#
# ──────────────────────────────────────────────────────────────
# 4. THREAT HISTORY
# ──────────────────────────────────────────────────────────────
#
#  Method : GET
#  URL    : http://localhost:8000/api/v1/history/logs?limit=20
#  Optional query params:
#    skip        (int)    — pagination offset
#    module_type (string) — 'intent' | 'audio' | 'document'
#
#  Note: Logs only appear after at least one detection call has
#  been made (intent, document scan, or audio stream).
#
# ══════════════════════════════════════════════════════════════
