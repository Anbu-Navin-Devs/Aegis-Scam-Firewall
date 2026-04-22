# 🛡️ Aegis Backend — Technical Documentation

The Aegis Backend is a high-performance, asynchronous FastAPI server designed to power real-time scam detection, document analysis, and audio deepfake verification. It serves as the bridge between the Flutter mobile application and advanced AI models hosted on NVIDIA NIM.

---

## 🏗️ Technical Architecture

The backend is built using a modern, scalable Python stack:

- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) for high-concurrency, type-safe API routing.
- **Asynchronous Engine:** [Uvicorn](https://www.uvicorn.org/) ASGI server.
- **AI Integration:** [NVIDIA NIM](https://www.nvidia.com/en-us/ai-data-science/generative-ai/nim/) (via OpenAI-compatible SDK) for Llama-3.3 and Llama-3.2 Vision.
- **Database (ORM):** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) with [asyncpg](https://magicstack.github.io/asyncpg/current/) for non-blocking PostgreSQL operations.
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/latest/) for strict request/response modeling.
- **Audio Processing:** [librosa](https://librosa.org/) and [NumPy](https://numpy.org/) for heuristic spectral analysis.

---

## 🔄 Core Workflows

### 1. Intent Analysis Workflow (NLP)
When a call transcript or SMS is sent to `/api/v1/analyze/intent`:
1.  **Validation:** FastAPI validates the input transcript using the `IntentRequest` schema.
2.  **AI Inference:** The `nvidia_service` calls the **Llama-3.3-70B-Instruct** model on NVIDIA NIM.
3.  **Tactic Detection:** The model analyzes the text for psychological pressure tactics (Urgency, Authority, Fear, etc.).
4.  **Response:** The result (is_scam, score, reason) is returned immediately to the mobile app.
5.  **Persistence (Async):** A `BackgroundTasks` entry is created to log the threat into the PostgreSQL database without delaying the mobile response.

### 2. Document Scanning Workflow (Vision)
When a legal document/PDF is uploaded to `/api/v1/document/scan`:
1.  **Pre-processing:** If the file is a PDF, `PyMuPDF` converts the first 5 pages into high-resolution PNG images in memory.
2.  **Vision Analysis:** The `nvidia_service` sends these images to **Llama-3.2-11B-Vision-Instruct**.
3.  **Legal Check:** The model scans for predatory clauses, class-action waivers, and hidden fees.
4.  **Reporting:** Returns a categorized risk level (SAFE, LOW, MEDIUM, HIGH, CRITICAL) along with specific flagged clauses.

### 3. Live Audio Monitoring (WebSocket)
For real-time protection during active calls via `ws://.../api/v1/live-audio/stream`:
1.  **Handshake:** The mobile app initiates a WebSocket connection and sends a sample rate handshake.
2.  **Streaming:** The app sends continuous binary chunks of PCM audio.
3.  **Spectral Analysis:** The `audio_service` extracts features like Spectral Flatness, Silence Ratios, and Pitch Variation.
4.  **Deepfake Detection:** The heuristic engine detects if the voice is synthetically generated (TTS).
5.  **Real-time Alerts:** Alerts are pushed back over the WebSocket every few seconds if a threat is detected.

---

## 📁 File Structure & Responsibilities

```text
backend/
├── app/
│   ├── api/v1/                 # Endpoints (Routes)
│   │   ├── analyze.py          # NLP logic for transcripts
│   │   ├── document.py         # Vision logic for PDFs/Images
│   │   ├── live_audio.py       # WebSocket streaming logic
│   │   └── history.py          # DB log retrieval
│   ├── core/
│   │   └── config.py           # Settings loader (.env support)
│   ├── crud/
│   │   └── crud_threat.py      # Database read/write logic
│   ├── db/
│   │   └── database.py         # Async engine & init_db logic
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy table definitions
│   │   └── schemas.py          # Pydantic API models
│   └── services/
│       ├── nvidia_service.py   # NIM AI orchestration
│       └── audio_service.py    # DSP/Audio analysis
├── .env                        # Local credentials (ignored by git)
└── requirements.txt            # System-wide dependencies
```

---

## 🚀 Setup & Deployment

### Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
NVIDIA_API_KEY=nvapi-xxxxxx
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aegis
DEBUG=True
```

### Running for Mobile Development
To ensure the mobile device can connect, you MUST bind the server to `0.0.0.0`:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🛠️ Error Handling & Resilience
- **Database Resilience:** The app uses a "Fail-Soft" database pattern. If PostgreSQL is unavailable, `init_db` will catch the connection error and log a warning, allowing the AI features to still function without persistence.
- **Type Safety:** 100% of incoming data is validated against Pydantic models to prevent injection attacks or invalid data crashes.
- **Async Execution:** Every I/O bound task (NVIDIA API calls, DB writes, File reads) is awaited using `asyncio` to prevent the server from blocking under high load.

---

## 📡 API Reference

| Endpoint | Method | Data Type | AI Model Used |
|----------|--------|-----------|---------------|
| `/health` | GET | - | - |
| `/api/v1/analyze/intent` | POST | JSON | Llama-3.3-70B |
| `/api/v1/document/scan` | POST | Multipart | Llama-3.2-11B Vision |
| `/api/v1/live-audio/stream` | WS | Binary | Spectral Heuristics |
| `/api/v1/history/logs` | GET | - | - |
