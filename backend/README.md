# 🛡️ Aegis Backend — FastAPI

The backend API server for Aegis: The Cognitive Scam Firewall.

## Tech Stack

- **Python 3.10+**
- **FastAPI** — async web framework
- **Uvicorn** — ASGI server
- **Google Gemini AI** — cognitive intent analysis
- **Pydantic** — data validation & settings management
- **PostgreSQL** — primary database *(future)*
- **Redis** — caching & task queue *(future)*

---

## 🚀 Quick Start

### 1. Create Virtual Environment

```powershell
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```powershell
# Copy the template to create your .env file
cp .env.template .env
```

**⚠️ CRITICAL:** Edit `.env` and add your **Google Gemini API Key**:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

> Get your API key from: https://makersuite.google.com/app/apikey

**🔒 NEVER commit the `.env` file to Git!** (already protected by `.gitignore`)

### 5. Run Development Server

```powershell
uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

---

## 📡 API Endpoints

### System Health

- **GET** `/health` — Server liveness check

### Intent Analysis (v1)

- **POST** `/api/v1/analyze/intent` — Analyze text for scam patterns

**Example Request:**
```json
{
  "transcript": "This is the IRS. You owe $5000 in back taxes. Pay immediately or face arrest."
}
```

**Example Response:**
```json
{
  "is_scam": true,
  "scam_score": 95,
  "reason": "High-pressure urgency tactics detected: mentions immediate payment, threatens legal action, impersonates authority figure (IRS). Classic social engineering pattern."
}
```

---

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── analyze.py       # Intent analysis endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # Environment settings (Pydantic)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py    # Google Gemini AI integration
│   └── main.py                  # FastAPI app initialization
├── tests/                       # Unit & integration tests
├── .env.template                # Environment variable template
├── .env                         # Your actual credentials (NEVER COMMIT!)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🧪 Testing the API

### Using cURL

```powershell
# Health check
curl http://localhost:8000/health

# Intent analysis
curl -X POST http://localhost:8000/api/v1/analyze/intent `
  -H "Content-Type: application/json" `
  -d '{"transcript": "Congratulations! You won $1,000,000! Click here now!"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze/intent",
    json={"transcript": "Your bank account has been frozen. Call us immediately."}
)

print(response.json())
```

---

## 🔒 Security Notes

1. **Never commit `.env` file** — already excluded by `.gitignore`
2. **CORS is currently set to `allow_origins=["*"]`** for development
   - ⚠️ Restrict this in production to specific domains only
3. **API keys should be rotated periodically**
4. **Use HTTPS in production**

---

## 🚧 Roadmap

- [ ] Add database integration (PostgreSQL)
- [ ] Implement Redis caching for AI responses
- [ ] Add deepfake audio/video detection module
- [ ] Implement honeypot defense system
- [ ] Add user authentication & JWT tokens
- [ ] Rate limiting & request throttling
- [ ] Comprehensive test coverage

---

## 📝 Development Guidelines

- Always work within `/backend` to avoid merge conflicts with frontend
- Write tests for new endpoints
- Use type hints for all function parameters/returns
- Document new endpoints in this README
- Follow PEP 8 style guidelines

---

**Aegis Backend** — Intelligent scam detection at scale. 🛡️


