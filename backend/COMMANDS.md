# 📋 Aegis Backend — Part 2 Terminal Commands

## Complete Setup & Run Commands (Windows PowerShell)

### 1️⃣ Install Dependencies

```powershell
cd "E:\ANDROID STUDIO\Aegis-Scam-Firewall\backend"

# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Install the new dependencies
pip install google-generativeai pydantic-settings python-dotenv
```

**OR** install everything from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

### 2️⃣ Create Environment File

```powershell
# Copy template to .env
Copy-Item .env.template .env
```

Then **MANUALLY EDIT** `backend\.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
ENV=development
DEBUG=True
```

> Get API key from: https://makersuite.google.com/app/apikey

---

### 3️⃣ Run the Server with Reload

```powershell
cd "E:\ANDROID STUDIO\Aegis-Scam-Firewall\backend"
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### 4️⃣ Test the API

**Open browser:**
```
http://localhost:8000/docs
```

**OR use cURL:**
```powershell
curl -X POST http://localhost:8000/api/v1/analyze/intent `
  -H "Content-Type: application/json" `
  -d '{\"transcript\": \"This is the IRS. You owe money. Pay now or face arrest.\"}'
```

**OR use Invoke-RestMethod (PowerShell native):**
```powershell
$body = @{
    transcript = "Your bank account has been compromised. Click here immediately."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze/intent" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `.\venv\Scripts\Activate.ps1` | Activate virtual environment |
| `pip install -r requirements.txt` | Install all dependencies |
| `uvicorn app.main:app --reload` | Run development server |
| `deactivate` | Deactivate virtual environment |

---

## 🔍 Verify Installation

```powershell
# Check if packages installed correctly
pip list | Select-String "google-generativeai|pydantic-settings"
```

Expected output:
```
google-generativeai    0.3.x
pydantic-settings      2.x.x
```

---

## 📡 Available Endpoints

- `GET /health` — System health check
- `GET /docs` — Interactive API documentation (Swagger)
- `GET /redoc` — Alternative API documentation (ReDoc)
- `POST /api/v1/analyze/intent` — Scam intent analysis

---

**🚀 Ready to go!** Run `uvicorn app.main:app --reload` and visit http://localhost:8000/docs

