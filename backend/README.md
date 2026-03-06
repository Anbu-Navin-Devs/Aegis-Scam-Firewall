# 🛡️ Aegis Backend — FastAPI

The backend API server for Aegis: The Cognitive Scam Firewall.

## Tech Stack

- **Python 3.10+**
- **FastAPI** — async web framework
- **Uvicorn** — ASGI server
- **PostgreSQL** — primary database
- **Redis** — caching & task queue

## Quick Start

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/            # Route handlers
│   ├── core/           # Config, security, dependencies
│   ├── models/         # Database & Pydantic models
│   ├── services/       # Business logic & AI modules
│   └── main.py         # FastAPI entry point
├── tests/              # Unit & integration tests
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

