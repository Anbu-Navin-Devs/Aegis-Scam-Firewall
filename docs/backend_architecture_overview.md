# Professional Architecture Overview: Aegis Backend

This document outlines the current state of the backend architecture for **Aegis: The Cognitive Scam Firewall**, designed for seamless handoff between AI/Backend and Frontend development teams.

---

## 📂 Current File Structure

The backend employs a modular `FastAPI` structure optimized for microservice scalability and separation of concerns.

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── analyze.py        # Intent analysis endpoints
│   │       ├── deepfake.py       # Audio deepfake detection endpoints
│   │       ├── document.py       # Document/PDF scanning endpoints
│   │       ├── history.py        # Threat history log endpoints
│   │       └── live_audio.py     # Real-time WebSocket audio stream
│   ├── core/
│   │   └── config.py             # Pydantic Settings (.env loader)
│   ├── crud/
│   │   └── crud_threat.py        # Database CRUD operations
│   ├── db/
│   │   └── database.py           # Async SQLAlchemy engine & session
│   ├── models/
│   │   ├── db_models.py          # SQLAlchemy ORM models
│   │   └── schemas.py            # Pydantic validation schemas
│   ├── services/
│   │   ├── audio_service.py      # Core audio feature extraction
│   │   └── nvidia_service.py     # NVIDIA NIM LLM integration
│   └── main.py                   # FastAPI app entry point
├── .env                          # Environment variables (git-ignored)
├── .env.example                  # Environment template
├── README.md                     # Backend-specific readme
└── requirements.txt              # Python dependencies
```

---

## ⚙️ Logic Mapping

A summary of exactly what the existing Python modules are doing:

- **`main.py`**: The heart of the application. It initializes the FastAPI instance, configures global CORS middleware, creates a `/health` endpoint for uptime monitoring, and registers all `/api/v1` routers. Uses async lifespan for DB schema creation on startup.
- **`api/v1/analyze.py`**: Exposes the REST route receiving transcription text (from SMS or calls) and passes them to the NVIDIA NIM Llama 3.3 engine to determine if the message is a scam.
- **`api/v1/deepfake.py`**: Exposes the REST routes responsible for receiving audio samples and passing them into the audio analysis pipeline.
- **`api/v1/document.py`**: Handles PDF/image uploads for predatory clause detection. Converts PDFs to images via PyMuPDF for vision-based analysis.
- **`api/v1/history.py`**: Provides GET endpoints for querying persisted threat logs from the database.
- **`api/v1/live_audio.py`**: WebSocket endpoint for real-time audio streaming and deepfake detection during live calls.
- **`models/schemas.py`**: Defines strict Pydantic objects (`IntentRequest`, `IntentResponse`, `DeepfakeResponse`, `DocumentAnalysisResponse`). These ensure that requests from the Flutter app are strictly typed and automatically generate the Swagger UI documentation.
- **`services/audio_service.py`**: Contains the mathematical and ML logic for analyzing audio liveness (extracting spectral flatness, silence ratios, and pitch variations) to detect text-to-speech synthesis.
- **`services/nvidia_service.py`**: Wraps the NVIDIA NIM API (via OpenAI-compatible client) to power both the NLP intent analysis engine (Llama 3.3 70B) and the document vision analysis (Llama 3.2 11B Vision).

---

## 🌉 Integration Status

### ✅ Completed
1. **WebSocket Integration for Real-Time Audio** — `live_audio.py` provides a WebSocket endpoint for continuous audio chunk streaming.
2. **Data Persistence (ORM)** — SQLAlchemy async models and CRUD layer implemented for threat log persistence.
3. **Document Scanning** — PDF-to-image conversion via PyMuPDF with vision-model analysis for predatory clause detection.
4. **NVIDIA NIM Migration** — Full migration from Google Gemini to NVIDIA NIM (Llama 3.3 + Llama 3.2 Vision).

### ⚠️ Known Limitations
1. **CORS Policy** — Currently set to `allow_origins=["*"]` for development. Must be restricted for production.
2. **Database** — Requires a running PostgreSQL instance. Background task logging will silently fail without one.

---

## 📡 Available API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/docs` | Interactive Swagger UI |
| `POST` | `/api/v1/analyze/intent` | Scam intent analysis |
| `POST` | `/api/v1/deepfake/analyze` | Audio deepfake detection |
| `POST` | `/api/v1/document/scan` | Document/PDF scanning |
| `GET` | `/api/v1/history/logs` | Threat history logs |
| `WS` | `/api/v1/live-audio/stream` | Real-time audio WebSocket |

---

## 🤝 Developer Contract (Response JSON)

The following JSON schema represents the target "Developer Contract". This is the exact payload the FastAPI backend sends to the Flutter frontend when querying a combined **Threat Report**.

```json
{
  "status": "success",
  "request_id": "req-98x4-ae32-11ef",
  "timestamp": "2026-04-13T16:30:00Z",
  "threat_report": {
    "is_scam_active": true,
    "combined_risk_score": 88.5,
    "intent_analysis": {
      "is_malicious": true,
      "confidence": 92.0,
      "reason": "High-pressure urgency tactics detected: impersonates the IRS and demands immediate payment."
    },
    "audio_analysis": {
      "is_deepfake": true,
      "confidence": 85.0,
      "details": "Spectral flatness is abnormally uniform (0.92) suggesting typical TTS synthesised speech."
    },
    "recommended_action": "BLOCK_CALLER"
  }
}
```
