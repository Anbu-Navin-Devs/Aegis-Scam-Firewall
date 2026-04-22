# Aegis Backend — FastAPI Server

The core backend service for **Aegis: The Cognitive Scam Firewall**.

## Quick Start

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env → add your NVIDIA_API_KEY

# 4. Start server (accessible from mobile devices)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVIDIA_API_KEY` | ✅ Yes | NVIDIA NIM API key for Llama models |
| `DATABASE_URL` | ❌ No | PostgreSQL async connection string |
| `ENV` | ❌ No | `development` or `production` |
| `DEBUG` | ❌ No | Enable debug logging |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/api/v1/analyze/intent` | Scam intent analysis |
| `POST` | `/api/v1/deepfake/analyze` | Audio deepfake detection |
| `POST` | `/api/v1/document/scan` | PDF/image predatory clause scan |
| `GET` | `/api/v1/history/logs` | Threat history logs |
| `WS` | `/api/v1/live-audio/stream` | Real-time audio WebSocket |

## AI Models

| Task | Model | Provider |
|------|-------|----------|
| Intent Analysis | `meta/llama-3.3-70b-instruct` | NVIDIA NIM |
| Document Vision | `meta/llama-3.2-11b-vision-instruct` | NVIDIA NIM |
| Audio Deepfake | Heuristic (spectral analysis) | Local (librosa) |

## Dependencies

Key packages in `requirements.txt`:

- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `openai` — NVIDIA NIM client (OpenAI-compatible)
- `PyMuPDF` — PDF to image conversion
- `librosa` — Audio feature extraction
- `sqlalchemy` + `asyncpg` — Async PostgreSQL ORM
