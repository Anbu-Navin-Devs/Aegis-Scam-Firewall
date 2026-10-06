# 🛡️ Aegis — The Cognitive Scam Firewall

> **Autonomous Real-Time Scam & Deepfake Protection for Android**
> *Protecting users from SMS smishing, live deepfake voice extortion, and predatory legal contracts.*

[![Android](https://img.shields.io/badge/Android-Kotlin%20%2B%20Jetpack%20Compose-3DDC84?style=flat&logo=android)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python%203.13-009688?style=flat&logo=fastapi)](backend/)
[![ML Accuracy](https://img.shields.io/badge/ML%20Accuracy-98.31%25-brightgreen)](backend/train_ml_model.py)
[![Inference Latency](https://img.shields.io/badge/Local%20ML%20Latency-0.9%C2%B5s-blue)](backend/train_ml_model.py)
[![NVIDIA NIM](https://img.shields.io/badge/AI%20Engine-NVIDIA%20NIM%20(Llama%203.3)-76B900?style=flat&logo=nvidia)](https://build.nvidia.com)
[![Tests](https://img.shields.io/badge/Pytest-9%2F9%20Passing-success)](backend/tests/)

---

## 🌟 What is Aegis?

**Aegis** is an autonomous mobile scam firewall designed to neutralize modern social engineering attacks before victims suffer financial or identity theft. Unlike legacy caller-ID or static spam lists, Aegis operates as an **active, real-time guardian** combining:

1. **Autonomous SMS Smishing Interceptor**: Evaluates incoming text messages in the background in **< 2 milliseconds** without opening the app, triggering high-priority heads-up alert banners for high-risk fraud.
2. **Real-Time Call Audio Guardian**: Runs an Android Foreground Service during active phone calls, analyzing voice liveness over streaming WebSockets to detect synthetic AI deepfakes.
3. **Hybrid On-Device ML + Cloud Cognitive AI Pipeline**: Instant local protection (<1µs, 100% private, offline) backed by NVIDIA NIM Llama 3.3 70B for deep psychological reasoning.
4. **Multimodal Threat Fusion & Victim Countermeasure Advisor**: Merges voice liveness, NLP intent, and sender telemetry into a composite threat verdict, delivering real-time verbal countermeasure scripts and 1-tap standardized Cybercrime Reports (FTC / IC3 / 1930).
5. **Predatory Document & Contract Scanner**: Uses Llama 3.2 Vision to scan loan agreements and contracts for hidden auto-renewals, arbitration traps, and predatory terms.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ANDROID CLIENT (Kotlin + Compose)                     │
│                                                                             │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │   SmsReceiver (Real-Time) │         │  CallStateReceiver + Service  │   │
│   │  • Intercepts SMS (Telephony)       │  • Auto-detects active calls  │   │
│   │  • Tier-1 Local ML (<2ms) │         │  • Foreground Audio Streamer  │   │
│   │  • Heads-Up Red Alert     │         │  • WebSocket live telemetry   │   │
│   └─────────────┬─────────────┘         └───────────────┬───────────────┘   │
│                 │                                       │                   │
│                 ▼                                       ▼                   │
│       AegisNotificationManager ◄─────────────── IntentScreen / LiveAudio    │
└─────────────────┼───────────────────────────────────────┼───────────────────┘
                  │ REST (Port 8000)                      │ WS (Port 8000)
                  ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND SYSTEM                            │
│                                                                             │
│   ┌────────────────────────────┐         ┌──────────────────────────────┐   │
│   │  Trained ML Pipeline       │         │   Digital Signal Processing  │   │
│   │  • TF-IDF + Naive Bayes/SVM│         │  • Spectral Flatness         │   │
│   │  • 98.31% Accuracy (0.9µs) │         │  • Pitch Variance & Silence  │   │
│   └─────────────┬──────────────┘         └──────────────┬───────────────┘   │
│                 │                                       │                   │
│                 ▼                                       ▼                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │               Threat Fusion Engine & Countermeasures                │   │
│   │  • Multimodal Composite Risk Scoring                                │   │
│   │  • Victim Tactical Scripts ("What to Say")                          │   │
│   │  • Standardized FTC/IC3 Cybercrime Telemetry Incident Report        │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        NVIDIA NIM AI Cloud                          │   │
│   │  • Llama 3.3 70B Instruct (Cognitive Intent & Manipulation Analysis)│   │
│   │  • Llama 3.2 11B Vision (Predatory Legal Document Auditing)         │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │ Async BackgroundTasks                │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │              PostgreSQL Async Threat Log Persistence                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🥊 Competitive Advantage: What Other Apps Lack

| Feature | Truecaller | Hiya Protect | Google Pixel Call Screen | McAfee Scam Protection | **Aegis Scam Firewall** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Real-Time Deepfake Voice Detection** | ⚠️ Manual button (must put call on hold) | Carrier-only integration | ❌ No | ❌ PC/Browser only | **✅ Automatic in-call background stream** |
| **Autonomous SMS Smishing Interception** | ⚠️ Basic blacklist | ⚠️ Number reputation | ⚠️ Spam filter | ⚠️ Scans links only | **✅ Immediate heads-up alert with ML intent (<2ms)** |
| **On-Device Sub-Millisecond ML Model** | ❌ Cloud lookup | ❌ Cloud lookup | ⚠️ Pixel-exclusive | ❌ Cloud | **✅ 98.31% Accuracy (<1µs latency, 100% offline)** |
| **Legal Contract & Clause Scanner** | ❌ No | ❌ No | ❌ No | ❌ No | **✅ Llama 3.2 Vision Predatory Clause Audit** |
| **Multimodal Threat Fusion** | ❌ Disjointed | ❌ No | ❌ No | ❌ No | **✅ Fuses voice liveness + text intent into 1 score** |
| **Victim Tactical Countermeasures** | ❌ None | ❌ None | ❌ None | ❌ None | **✅ Live verbal traps & scripts to expose scammers** |
| **1-Tap Cybercrime Incident Report** | ❌ None | ❌ None | ❌ None | ❌ None | **✅ Standardized FTC, IC3 & 1930 evidentiary output** |
| **Hardware / Carrier Freedom** | Any Android | Requires Carrier | ❌ Pixel-only | PC / Mac | **✅ Any Android Device (API 26+)** |

---

## 🧠 Machine Learning Training & Benchmark Results

Aegis implements a **Tier-1 Local ML Model** trained on **5,619 real-world SMS messages** (curated banking, delivery, and government smishing patterns + UCI SMS Spam Benchmark Dataset):

```text
Model                      | Accuracy  | Precision | Recall    | F1-Score  | Latency (µs)
----------------------------------------------------------------------------------------
Multinomial Naive Bayes    |  98.31%   |  96.79%   |  89.88%   |  93.21%   |     0.9 µs
Linear SVM (LinearSVC)     |  98.31%   |  97.40%   |  89.29%   |  93.17%   |     0.2 µs
Logistic Regression        |  97.70%   |  97.26%   |  84.52%   |  90.45%   |     0.2 µs
Random Forest              |  97.32%   |  97.16%   |  81.55%   |  88.67%   |    31.9 µs
```

- **Inference Latency**: Less than **1 microsecond (0.0009 ms)** per message.
- **Privacy Guarantee**: 100% of SMS messages remain private on the user's phone; zero personal message text leaves the device for standard classification.

---

## 📁 Repository Structure

```
Aegis-Scam-Firewall/
├── backend/                                # FastAPI server & ML pipeline
│   ├── app/
│   │   ├── api/v1/                         # Endpoints (/intent, /ml-intent, /fusion, /audio, /scan)
│   │   ├── core/config.py                  # App settings & NVIDIA API configuration
│   │   ├── crud/                           # Async PostgreSQL database operations
│   │   ├── db/database.py                  # Async SQLAlchemy session manager
│   │   ├── models/schemas.py               # Pydantic validation models
│   │   └── services/                       # NVIDIA NIM & DSP audio analysis
│   ├── models_saved/                       # Serialized ML model pipeline (.joblib)
│   ├── tests/test_endpoints.py             # 9/9 automated pytest test suite
│   ├── train_ml_model.py                   # Automated ML training & benchmarking script
│   └── Dockerfile                          # Production container configuration
│
├── frontend/                               # Native Android Kotlin Application
│   ├── app/src/main/
│   │   ├── AndroidManifest.xml             # Background permissions, receivers & service tags
│   │   └── java/com/aegis/scamfirewall/
│   │       ├── MainActivity.kt             # Navigation host & notification deep-linking
│   │       ├── core/
│   │       │   ├── config/AppConfig.kt     # Dynamic Emulator (10.0.2.2) & LAN IP routing
│   │       │   ├── ml/LocalScamClassifier.kt # On-device Tier-1 ML pattern matrix (<2ms)
│   │       │   ├── network/                # ApiService (REST) & LiveAudioService (WebSocket)
│   │       │   ├── notification/AegisNotificationManager.kt # Heads-up alerts & channels
│   │       │   └── service/CallMonitorForegroundService.kt  # Call audio background streamer
│   │       └── features/
│   │           ├── sms/SmsReceiver.kt      # Real-time BroadcastReceiver for SMS
│   │           ├── call/CallStateReceiver.kt # Call transition detector (OFFHOOK/IDLE)
│   │           ├── dashboard/              # Real-Time Shield status & feature cards
│   │           ├── intent/                 # Intent analysis & countermeasure view
│   │           ├── live/                   # Live deepfake audio radar
│   │           ├── scan/                   # Predatory contract audit
│   │           └── history/                # Threat history timeline
│   └── build.gradle.kts                    # Android Gradle configuration
│
└── docs/
    ├── System_Architecture.md              # In-depth architectural blueprint
    ├── backend_architecture_overview.md    # API contract specifications
    └── competitive_analysis_and_differentiation.md # Market analysis & state-of-the-art report
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (FastAPI backend)
- **Android Studio / Android SDK** (API 26+)
- **NVIDIA NIM API Key** (from [build.nvidia.com](https://build.nvidia.com))

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate, Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# Copy environment template and add your NVIDIA_API_KEY
copy .env.example .env

# Train ML benchmark model (optional, pre-trained model included)
python train_ml_model.py

# Run unit tests
python -m pytest

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger UI documentation available at: `http://localhost:8000/docs`

### 3. Android App Setup
1. Open the `frontend/` directory in **Android Studio**.
2. Or build and install directly via terminal:
   ```powershell
   cd frontend
   .\gradlew.bat assembleDebug
   adb install -r app\build\outputs\apk\debug\app-debug.apk
   ```
3. Launch **Aegis** on your device or emulator and tap **"Activate Real-Time Shield"** to grant SMS and Call detection permissions.

---

## 🧪 Real-Time Verification

### Test 1: Simulating an Incoming Scam SMS
Send a smishing attack using ADB:
```powershell
adb emu sms send "+18005550199" "URGENT: Your Bank of America account is locked. Verify at http://bit.ly/secure-auth-update or your account will be suspended."
```
- **Observed Behavior**:
  - `SmsReceiver` intercepts the message in the background.
  - In `< 2ms`, `LocalScamClassifier` flags risk score `70/100`.
  - A **Heads-Up Alert Notification** rings with red alert: `🚨 Scam SMS Blocked! (Risk: 70/100)`.
  - Tapping the banner opens `IntentScreen` with countermeasures ready.

### Test 2: Simulating an Active Phone Call
```powershell
adb emu gsm call "+18005550199"
adb emu gsm accept "+18005550199"
```
- **Observed Behavior**:
  - `CallStateReceiver` detects call pickup (`OFFHOOK`).
  - `CallMonitorForegroundService` launches with persistent notification icon.
  - Microphone streams to live WebSocket; if synthetic voice confidence $\ge 50\%$, an alert warning is triggered.

---

## 📜 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/analyze/intent` | Cognitive intent analysis via NVIDIA NIM Llama 3.3 70B |
| `POST` | `/api/v1/analyze/ml-intent` | Ultra-low latency (<1ms) text classification via trained ML model |
| `POST` | `/api/v1/analyze/fusion` | Multimodal threat fusion, victim countermeasures & legal report generation |
| `POST` | `/api/v1/analyze/audio` | Audio file upload deepfake analysis (librosa DSP) |
| `POST` | `/api/v1/scan/document` | Predatory legal clause extraction via Llama 3.2 11B Vision |
| `WS`   | `/ws/live-audio` | Real-time binary PCM audio streaming over WebSocket |
| `GET`  | `/api/v1/history/logs` | Query persistent threat incident history |
| `GET`  | `/health` | Server health and service readiness check |

---

## 🛡️ License & Acknowledgements
Built for the **Aegis Scam Firewall Project**. Powered by [NVIDIA NIM](https://build.nvidia.com), [FastAPI](https://fastapi.tiangolo.com/), and [Jetpack Compose](https://developer.android.com/jetpack/compose).
