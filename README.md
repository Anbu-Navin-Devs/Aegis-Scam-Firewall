# 🛡️ Aegis — The Cognitive Scam Firewall

> **AI-Powered Real-Time Scam Detection for Mobile Devices**

Aegis is an end-to-end mobile security platform that uses advanced AI models to detect scam calls, fraudulent messages, deepfake audio, and predatory legal documents — all in real-time, directly on your Android device.

> ⚠️ **PROJECT UNDER CONSTRUCTION** ⚠️
> 
> **Status:** Backend functionality is complete and verified.
> **Current Issue:** The mobile frontend is currently experiencing intermittent `Connection timed out` and `Software caused connection abort (OS Error: 103/110)` issues when deployed to physical Android devices via ADB Wireless. These socket connection errors are preventing the Flutter frontend from maintaining stable communication with the local Python backend over the network.
> **Work in Progress:** We are actively debugging the Android networking constraints and local IP routing. In the meantime, backend endpoints can be tested via `localhost:8000/docs`.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Flutter Mobile App                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Intent   │ │ Deepfake │ │ Document │ │ Live Audio │ │
│  │ Analysis │ │ Detector │ │ Scanner  │ │  Monitor   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘ │
│       │ REST        │ REST       │ REST         │ WS     │
└───────┼─────────────┼────────────┼──────────────┼────────┘
        │             │            │              │
┌───────▼─────────────▼────────────▼──────────────▼────────┐
│                   FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────┐    │
│  │              NVIDIA NIM AI Engine                 │    │
│  │  • Llama 3.3 70B (Intent Analysis)               │    │
│  │  • Llama 3.2 11B Vision (Document Scanning)      │    │
│  │  • Heuristic Audio Pipeline (Deepfake Detection)  │    │
│  └──────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────┐    │
│  │              PostgreSQL (Threat Logs)              │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Module | Description | AI Model |
|--------|-------------|----------|
| **Intent Analysis** | Detects scam patterns in SMS, call transcripts, and emails | Llama 3.3 70B Instruct |
| **Document Scanner** | Identifies predatory clauses in contracts, loans, and legal PDFs | Llama 3.2 11B Vision |
| **Deepfake Detection** | Analyzes audio samples for synthetic speech indicators | Heuristic (librosa) |
| **Live Audio Monitor** | Real-time WebSocket stream for call monitoring | Heuristic (librosa) |
| **Threat History** | Persistent log of all detected threats | PostgreSQL |

---

## 📁 Project Structure

```
Aegis-Scam-Firewall/
├── backend/                    # Python FastAPI server
│   ├── app/
│   │   ├── api/v1/             # REST + WebSocket endpoints
│   │   ├── core/config.py      # Environment configuration
│   │   ├── crud/               # Database CRUD operations
│   │   ├── db/                 # Async SQLAlchemy engine
│   │   ├── models/             # Pydantic schemas + ORM models
│   │   └── services/           # AI service layer
│   │       ├── nvidia_service.py   # NVIDIA NIM (Llama) integration
│   │       └── audio_service.py    # Audio feature extraction
│   ├── .env                    # API keys (git-ignored)
│   ├── .env.example            # Template for new developers
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Flutter mobile application
│   ├── lib/
│   │   ├── core/config/        # Backend URL configuration
│   │   ├── core/network/       # HTTP & WebSocket services
│   │   └── features/           # UI screens per module
│   └── android/                # Android build configuration
│
├── docs/                       # Technical documentation
│   ├── System_Architecture.md
│   ├── backend_architecture_overview.md
│   └── error_handling.md
│
├── install_to_mobile.py        # Automated wireless deployment script
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend server |
| Flutter SDK | 3.24+ | Mobile app build |
| ADB | Latest | Android device communication |
| PostgreSQL | 15+ | Threat log persistence (optional) |

### 1. Backend Setup

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your NVIDIA_API_KEY

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **⚠️ IMPORTANT:** The backend MUST be started with `--host 0.0.0.0` so that your mobile device can reach it over the local network.

### 2. Mobile Deployment

The `install_to_mobile.py` script automates the entire wireless deployment process:

```powershell
# Edit the script with your device's Wireless Debugging info
# (IP, pairing port, pairing code, connect port)
python install_to_mobile.py
```

The script will:
1. ✅ Auto-detect connected ADB devices
2. ✅ Pair and connect if needed
3. ✅ Download Flutter SDK if not installed (to `C:\flutter_sdk`)
4. ✅ Build and deploy the APK to your phone

### 3. Environment Variables

Create `backend/.env` with:

```env
# NVIDIA NIM API Key (required)
NVIDIA_API_KEY=nvapi-your-key-here

# Application Settings
ENV=development
DEBUG=True

# Database (optional — app works without it, logs won't persist)
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aegis
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/docs` | Interactive Swagger UI |
| `POST` | `/api/v1/analyze/intent` | Analyze text for scam patterns |
| `POST` | `/api/v1/deepfake/analyze` | Analyze audio for deepfake |
| `POST` | `/api/v1/document/scan` | Scan PDF/image for predatory clauses |
| `GET` | `/api/v1/history/logs` | Get threat history |
| `WS` | `/api/v1/live-audio/stream` | Real-time audio monitoring |

### Example: Intent Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze/intent \
  -H "Content-Type: application/json" \
  -d '{"transcript": "URGENT: You owe $5000. Pay with gift cards now or face arrest."}'
```

**Response:**
```json
{
  "is_scam": true,
  "scam_score": 92,
  "reason": "Multiple high-pressure tactics detected: urgency, authority impersonation (IRS), and financial demands via untraceable payment methods."
}
```

---

## 🔧 Frontend Configuration

The Flutter app connects to the backend via the IP address configured in:

```
frontend/lib/core/config/app_config.dart
```

```dart
class AppConfig {
  // Set this to your computer's local IPv4 address
  static const String devBaseUrl = 'http://YOUR_PC_IP:8000';
  static const String devWsUrl = 'ws://YOUR_PC_IP:8000';
}
```

> **Finding your IP:** Run `ipconfig` in PowerShell and use your Wi-Fi adapter's IPv4 address.

---

## ⚠️ Known Issues & Limitations

### Frontend (Flutter)

| Issue | Status | Notes |
|-------|--------|-------|
| `Connection timed out` errors | **Expected** | The backend must be running before opening the app. Start the backend first. |
| `performTraversals: cancelAndRedraw` log spam | **Cosmetic** | Android system-level rendering messages. Does not affect functionality. |
| Live Audio Monitor stuck on "Awaiting backend stream" | **Expected** | Backend must be running with `--host 0.0.0.0` for the phone to reach it. |
| SDK version warnings during build | **Non-blocking** | `compileSdk` and `ndkVersion` warnings are advisory; the app still builds and installs successfully. |

### Backend (Python)

| Issue | Status | Notes |
|-------|--------|-------|
| Database connection failures (SQLAlchemy) | **Non-blocking** | If PostgreSQL isn't running, the app still works — threat logs just won't persist. Errors are caught and logged silently. |
| PDF processing for large documents | **Limited** | Only the first 5 pages are analyzed to keep payload sizes reasonable for the vision model. |

### Deployment (ADB / Flutter)

| Issue | Status | Notes |
|-------|--------|-------|
| Wireless Debugging ports change | **Expected** | Android generates new ports each time you toggle Wireless Debugging. Update `install_to_mobile.py` accordingly. |
| `flutter` not found in PATH | **Auto-resolved** | The install script auto-downloads Flutter SDK to `C:\flutter_sdk` if not found. |

---

## ✅ Testing & Verification

### Backend Verification

```powershell
# 1. Start the server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"Aegis Backend is Active","version":"1.0.0"}

# 3. Test intent analysis
curl -X POST http://localhost:8000/api/v1/analyze/intent \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Hello, this is your bank. Your account is compromised."}'

# 4. Open interactive docs
# Visit: http://localhost:8000/docs
```

### Mobile Verification

1. Ensure backend is running with `--host 0.0.0.0 --port 8000`
2. Run `python install_to_mobile.py`
3. Open the app on your phone
4. Test each feature:
   - **Intent Analysis**: Enter any suspicious text → tap "Analyze Intent"
   - **Document Scanner**: Upload a PDF → view flagged clauses
   - **Live Audio Monitor**: Opens WebSocket connection to backend
   - **Threat History**: Shows previously logged threats

---

## 🛠️ Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Python + FastAPI | 3.10+ / 0.110+ |
| **AI (Text)** | NVIDIA NIM — Llama 3.3 70B Instruct | via OpenAI SDK |
| **AI (Vision)** | NVIDIA NIM — Llama 3.2 11B Vision | via OpenAI SDK |
| **Audio Analysis** | librosa + numpy | Heuristic pipeline |
| **PDF Processing** | PyMuPDF (fitz) | 1.24+ |
| **Database** | PostgreSQL + SQLAlchemy (async) | 15+ / 2.0+ |
| **Frontend** | Flutter (Dart) | 3.24+ |
| **Deployment** | ADB Wireless Debugging | Android 11+ |

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
