# Professional Architecture Overview: Aegis Backend

This document outlines the architecture and API specifications of the **Aegis Scam Firewall Backend**, designed for seamless interoperability between Backend, Machine Learning, and Android Mobile engineering teams.

---

## 📂 File Structure

The backend employs an async `FastAPI` modular architecture optimized for high-concurrency microservices, sub-millisecond local ML inference, and streaming WebSockets:

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── analyze.py        # /intent (LLM), /ml-intent (ML), /fusion (Threat Fusion)
│   │       ├── deepfake.py       # Audio deepfake file upload endpoints
│   │       ├── document.py       # PDF/image document scanning endpoints
│   │       ├── history.py        # Threat history log endpoints
│   │       └── live_audio.py     # Real-time WebSocket audio stream (/ws/live-audio)
│   ├── core/
│   │   └── config.py             # Pydantic Settings (.env loader & NVIDIA config)
│   ├── crud/
│   │   └── crud_threat.py        # Database CRUD operations
│   ├── db/
│   │   └── database.py           # Async SQLAlchemy engine & session manager
│   ├── models/
│   │   ├── db_models.py          # SQLAlchemy ORM models (ThreatLog)
│   │   └── schemas.py            # Pydantic validation schemas
│   ├── services/
│   │   ├── audio_service.py      # Core DSP feature extraction (librosa)
│   │   └── nvidia_service.py     # NVIDIA NIM LLM integration (Llama 3.3 / 3.2)
│   └── main.py                   # FastAPI app entry point & CORS configuration
├── models_saved/
│   └── scam_classifier_model.joblib # Trained TF-IDF + Naive Bayes/SVM model
├── tests/
│   ├── conftest.py               # Test configuration & mock credentials
│   └── test_endpoints.py         # 9/9 passing automated pytest test suite
├── .env                          # Local environment variables
├── .env.example                  # Template configuration
├── Dockerfile                    # Production container specification
├── requirements.txt              # Python dependencies
└── train_ml_model.py             # Automated ML training and benchmark pipeline
```

---

## ⚙️ Module Responsibilities

- **`main.py`**: Initializes the FastAPI instance, attaches CORS middleware, provides `/health` monitoring, and mounts all `/api/v1` routers with optional `X-API-Key` authentication.
- **`api/v1/analyze.py`**:
  - `POST /api/v1/analyze/intent`: Performs cognitive social engineering analysis using NVIDIA NIM (Llama 3.3 70B).
  - `POST /api/v1/analyze/ml-intent`: Sub-millisecond text classification (<1ms) using the pre-trained TF-IDF + Naive Bayes pipeline (98.31% accuracy).
  - `POST /api/v1/analyze/fusion`: Correlates multimodal threat signals (voice liveness + text intent + sender info), generates victim tactical countermeasure scripts, and produces standardized legal Cybercrime Reports (FTC / IC3 / 1930).
- **`api/v1/deepfake.py`**: Analyzes uploaded audio files for vocoder uniformity, pitch flattening, and synthetic silence patterns.
- **`api/v1/document.py`**: Converts contracts and loan agreements to images via PyMuPDF and audits for predatory clauses using Llama 3.2 11B Vision.
- **`api/v1/history.py`**: Paginated retrieval of persistent threat logs.
- **`api/v1/live_audio.py`**: Handles low-latency binary PCM audio streams via WebSocket (`/ws/live-audio`).
- **`services/audio_service.py`**: Math and DSP engine for Wiener spectral flatness, pitch variability ($F_0$), and silence ratios.
- **`train_ml_model.py`**: Script that downloads the UCI SMS Spam benchmark (5,619 samples), trains Naive Bayes, LinearSVM, Logistic Regression, and Random Forest, and serializes the best pipeline.

---

## 📡 Available API Endpoints

| Method | Path | Response Type | Description |
|---|---|---|---|
| `GET` | `/health` | JSON | System status & service readiness |
| `GET` | `/docs` | OpenAPI UI | Interactive Swagger documentation |
| `POST` | `/api/v1/analyze/intent` | `IntentResponse` | Cognitive LLM analysis (Llama 3.3 70B) |
| `POST` | `/api/v1/analyze/ml-intent` | `IntentResponse` | Ultra-fast trained ML text classification (<1ms) |
| `POST` | `/api/v1/analyze/fusion` | `ThreatFusionResponse` | Multimodal threat fusion & victim countermeasure scripts |
| `POST` | `/api/v1/analyze/audio` | `DeepfakeResponse` | Audio file upload deepfake detection |
| `POST` | `/api/v1/scan/document` | `DocumentAnalysisResponse`| Predatory clause detection in PDF / image |
| `GET` | `/api/v1/history/logs` | `ThreatHistoryResponse`| Paginated threat log retrieval |
| `WS` | `/ws/live-audio` | Streaming JSON | Real-time WebSocket binary PCM stream |

---

## 🤝 Multimodal Threat Fusion Contract (`POST /api/v1/analyze/fusion`)

### Request Payload:
```json
{
  "transcript": "URGENT: IRS warrant issued. Pay with gift cards immediately.",
  "voice_deepfake_confidence": 0.85,
  "sender_or_caller": "+18005550199"
}
```

### Response Payload:
```json
{
  "composite_risk_score": 98,
  "threat_level": "CRITICAL",
  "is_scam": true,
  "primary_threat_vector": "Multimodal AI Voice Impersonation & Financial Extortion",
  "tactical_countermeasures": [
    "🚨 VOICE INTEGRITY ALERT: The caller's voice exhibits abnormal acoustic uniformity (synthetic AI). Ask a personal 'challenge question' only the real person would know.",
    "Hang up immediately and call the individual or family member back using your saved phone number.",
    "⚖️ LEGAL PROTOCOL: Federal agencies send official notifications via certified mail, never via urgent phone demands or gift card payments.",
    "🛑 EXTORTION PROTOCOL: Demands for payment in gift cards, crypto, or money wire are 100% fraudulent. Terminate communication immediately."
  ],
  "cybercrime_report_snippet": "--- CYBERCRIME INCIDENT TELEMETRY REPORT ---\nTimestamp: 2026-09-02 13:30:00 UTC\nReported Suspect / Source: +18005550199\nThreat Classification: CRITICAL (Risk Score: 98/100)\nPrimary Vector: Multimodal AI Voice Impersonation & Financial Extortion\nAcoustic Deepfake Probability: 85%\nTranscript Telemetry: \"URGENT: IRS warrant issued. Pay with gift cards immediately.\"\nSummary: Automated interception by Aegis Scam Firewall. Threat indicators matched coordinated social engineering protocols.\nReady for submission to: FTC (reportfraud.ftc.gov) / IC3 (ic3.gov) / Cybercrime Portal (1930)"
}
```
