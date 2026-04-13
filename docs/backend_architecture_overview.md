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
│   │       └── deepfake.py       # Audio analysis endpoints
│   ├── core/                     # Configuration & dependencies
│   ├── models/
│   │   └── schemas.py            # Pydantic validation schemas
│   ├── services/
│   │   ├── audio_service.py      # Core audio feature extraction
│   │   └── gemini_service.py     # LLM integration logic
│   └── main.py                   # FastAPI app entry point
├── tests/                        # Automated testing suite
├── .env.example                  # Environment template
├── COMMANDS.md                   # Dev workflow documentation
├── README.md                     # Backend-specific readme
└── requirements.txt              # System dependencies
```

---

## ⚙️ Logic Mapping

A summary of exactly what the existing Python modules are doing:

- **`main.py`**: The heart of the application. It initializes the FastAPI instance, configures global CORS middleware, creates a `/health` endpoint for uptime monitoring, and registers all `/api/v1` routers.
- **`api/v1/analyze.py`**: Exposes the REST routes receiving transcription text (from SMS or calls) and passes them to the NLP engine to determine if the message is a scam.
- **`api/v1/deepfake.py`**: Exposes the REST routes responsible for receiving audio samples and passing them into the audio analysis pipeline.
- **`models/schemas.py`**: Defines strict Pydantic objects (`IntentRequest`, `IntentResponse`, `DeepfakeResponse`). These ensure that requests from the Flutter app are strictly typed (e.g., rejecting strings where floats belong) and automatically generate the Swagger UI documentation.
- **`services/audio_service.py`**: Contains the mathematical and ML logic for analyzing audio liveness (extracting spectral flatness, silence ratios, and pitch variations) to detect text-to-speech synthesis.
- **`services/gemini_service.py`**: Wraps the LLM (Google Gemini) SDK to power the NLP intent analysis engine, processing transcripts to detect high-pressure psychology and social engineering.

---

## 🌉 The "Integration Gap" (Missing Components)

To fully connect this backend to the Flutter frontend and achieve production status, the following gaps must be resolved:

1. **WebSocket Integration for Real-Time Audio:** Deepfake analysis currently uses REST. For live calls, the frontend needs a WebSocket endpoint (`ws://.../api/v1/stream`) to send continuous audio chunks without the overhead of HTTP headers.
2. **CORS Hardening:** In `main.py`, CORS is currently set to `allow_origins=["*"]`. This must be restricted to the deployed Flutter web domains or explicitly configured for the mobile apps to prevent API abuse.
3. **Unified Threat Report Endpoint:** Currently, schemas only exist for isolated `Intent` and `Deepfake` responses. A unified aggregation endpoint is needed to combine these into an overarching threat profile.
4. **Data Persistence (ORM):** The `models` directory only contains API schemas. SQLAlchemy models and an async database engine are required to log threat events to PostgreSQL as detailed in the architecture.

---

## 🤝 Developer Contract (Response JSON)

The following JSON schema represents the target "Developer Contract". This is the exact payload the FastAPI backend will eventually send to the Flutter frontend when querying a combined **Threat Report**. 

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
