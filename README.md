<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:050505,25:121212,50:1a1a1a,75:121212,100:050505&height=260&section=header&text=🛡️%20Aegis&fontSize=80&fontColor=4ade80&animation=twinkling&fontAlignY=35&desc=The%20Cognitive%20Scam%20Firewall&descSize=22&descAlignY=58&descAlign=50" width="100%"/>

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=1000&color=4ade80&center=true&vCenter=true&multiline=true&repeat=false&width=900&height=70&lines=AI-Powered+Real-Time+Scam+Detection;Deepfake+Calls+%7C+Phishing+%7C+Social+Engineering+Defense" alt="Typing SVG" /></a>

<br/>

<p>
<img src="https://img.shields.io/badge/Backend%20Status-Fully%20Operational-22c55e?style=for-the-badge&labelColor=16a34a" alt="Backend Status"/>
<img src="https://img.shields.io/badge/Frontend%20Status-Development%20(WIP)-f59e0b?style=for-the-badge&labelColor=d97706" alt="Frontend Status"/>
</p>

<p>
<img src="https://img.shields.io/badge/🤖_AI-Deepfake%20Detection-22c55e?style=flat-square&labelColor=16a34a" alt="AI Detection"/>
<img src="https://img.shields.io/badge/🧠_NLP-Intent%20Analysis-3b82f6?style=flat-square&labelColor=2563eb" alt="Intent Analysis"/>
<img src="https://img.shields.io/badge/📄_AI-Document%20Scanning-8b5cf6?style=flat-square&labelColor=7c3aed" alt="Document Scanning"/>
<img src="https://img.shields.io/badge/🍯_AI-Honeypot%20(Roadmap)-gray?style=flat-square&labelColor=475569" alt="Document Scanning"/>
</p>

<p>
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
<img src="https://img.shields.io/badge/SQLAlchemy-2.0%20Async-red?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
<img src="https://img.shields.io/badge/PostgreSQL-15+-316192?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
<img src="https://img.shields.io/badge/WebSockets-Live%20Audio-f59e0b?style=flat-square&logo=websocket&logoColor=white" alt="WebSockets"/>
<img src="https://img.shields.io/badge/Flutter-3.19+-02569B?style=flat-square&logo=flutter&logoColor=white" alt="Flutter"/>
<img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License"/>
</p>

<br/>

<a href="#-getting-started">
  <img src="https://img.shields.io/badge/⚡_GET_STARTED-5_MIN_SETUP-16a34a?style=for-the-badge&labelColor=15803d" alt="Quick Start"/>
</a>
&nbsp;&nbsp;
<a href="#-api-endpoints">
  <img src="https://img.shields.io/badge/🤖_DEVELOPER_API-DOCS-2563eb?style=for-the-badge&labelColor=1d4ed8" alt="API Docs"/>
</a>
</div>

<br/>

---

## 🎯 What is Aegis?

**Aegis** is an intelligent, multi-layered scam firewall that leverages cutting-edge AI to protect users from evolving digital threats — including deepfake calls, social-engineering messages, predatory legal documents, and phishing attacks. It acts as a cognitive shield for the modern mobile user.

> ℹ️ **Project Status:** The core AI features and underlying **Backend API are 100% feature-complete** and ready for production handling. The **Flutter mobile frontend is currently under active development.**

### 🔑 Core Defense Pillars

| Pillar | Status | Implementation |
|:-------|:------:|:---------------|
| 🎭 **AI Deepfake Detection** | ✅ Live | Real-time heuristic analysis of audio streams via WebSocket (spectral flatness, pitch stability, ZCR). |
| 🧠 **Intent Analysis Engine** | ✅ Live | Gemini 1.5 Flash NLP classification of transcripts, SMS, and messages for psychological manipulation tactics. |
| 📄 **Predatory Clause Detection** | ✅ Live | Gemini Vision analysis of uploaded PDFs/images for hidden or unfair legal clauses. |
| 🗄️ **Threat Persistence** | ✅ Live | All detection events logged to PostgreSQL via async SQLAlchemy; queryable via the history API. |
| 🍯 **Honeypot Defense** | 🗓️ Roadmap | Automated LLM engagement with scammers to exhaust resources and gather threat intelligence. |

---

## 🏗️ System Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    Flutter Mobile App                        │
│              (Android / Material Design 3)                   │
├──────────────────────────────────────────────────────────────┤
│         REST  /  WebSocket  (versioned: /api/v1/...)        │
├──────────────────────────────────────────────────────────────┤
│                  FastAPI Backend (Python 3.10+)              │
│  ┌──────────────┬──────────────┬────────────┬─────────────┐  │
│  │  Intent      │  Live Audio  │  Document  │  History    │  │
│  │  /analyze    │  /live-audio │  /document │  /history   │  │
│  │  (Gemini)    │  (WebSocket) │  (Vision)  │  (PG CRUD)  │  │
│  └──────────────┴──────────────┴────────────┴─────────────┘  │
│           ↓ BackgroundTasks / asyncio.create_task            │
├──────────────────────────────────────────────────────────────┤
│         PostgreSQL 15+  (threat_logs — JSONB payload)        │
│         SQLAlchemy 2.0 Async  +  asyncpg driver              │
└──────────────────────────────────────────────────────────────┘
```

> **Async-First by Design:** Every database write (threat logging) is decoupled from the HTTP/WebSocket response path using FastAPI `BackgroundTasks` (REST endpoints) and `asyncio.create_task` (WebSocket). The client always receives its AI verdict at peak speed — the database persistence happens in parallel, with zero latency impact.

---

## ✨ Platform Features

<table>
<tr>
<td width="50%" valign="top">

### 🔍 Deepfake & Audio Analysis
> *Real-time media screening*

- WebSocket streaming (float32 PCM binary frames)
- 1-second rolling analysis windows
- Spectral flatness & pitch stability scoring
- Synthesised speech recognition (heuristic)
- Sub-100 ms response per window

</td>
<td width="50%" valign="top">

### 💬 Deep Intent Analysis
> *NLP-driven threat identification*

- Phishing, SMS spam & transcript analysis
- Psychological urgency tactic detection
- Impersonation & authority deceit flags
- Gemini 1.5 Flash — granular confidence scoring

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📄 Predatory Clause Detection
> *AI-powered legal document scanner*

- Upload PDF, PNG, or JPEG (up to 20 MB)
- Detects 10 categories of predatory clauses
- SAFE → CRITICAL risk-level verdict
- Full flagged-clause list with section refs

</td>
<td width="50%" valign="top">

### 📊 Threat History Dashboard
> *Queryable persistent log of all events*

- PostgreSQL-backed threat log (JSONB payload)
- Paginated `GET /history/logs` API
- Filter by module: intent / audio / document
- Full AI verdict stored per row — no extra lookups

</td>
</tr>
</table>

---

## ⚙️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Runtime** | Python 3.10+ |
| **API Framework** | FastAPI 0.110+ |
| **AI** | Google Gemini 1.5 Flash (intent + document vision) |
| **Audio ML** | librosa + soundfile (heuristic spectral analysis) |
| **Real-time** | WebSockets (native FastAPI) |
| **ORM** | SQLAlchemy 2.0 — fully async |
| **DB Driver** | asyncpg |
| **Database** | PostgreSQL 15+ (JSONB threat payloads) |
| **Config** | pydantic-settings — `.env` file |
| **Frontend** | Flutter 3.19+ (Dart) |

---

## 🌐 API Endpoints

All REST routes are versioned under `/api/v1`. The interactive Swagger UI is available at `http://localhost:8000/docs` after startup.

| Method | Route | Type | Request | Response |
|:------:|:------|:----:|:--------|:---------|
| `POST` | `/api/v1/analyze/intent` | REST | JSON body `{ "transcript": "..." }` | `{ is_scam, scam_score, reason }` |
| `POST` | `/api/v1/document/scan` | REST | Multipart `file` (PDF / PNG / JPEG, ≤ 20 MB) | `{ risk_level, flagged_clauses[], summary }` |
| `WS` | `/api/v1/live-audio/stream` | WebSocket | Handshake JSON → float32 PCM binary chunks | `{ is_deepfake, confidence_score, analysis_details, window_index, elapsed_ms }` |
| `GET` | `/api/v1/history/logs` | REST | Query params: `skip`, `limit`, `module_type` | `{ total, skip, limit, logs[] }` |
| `GET` | `/health` | REST | — | `{ status: "ok" }` |

### WebSocket Protocol (`/live-audio/stream`)
```
Client → Server  (text)   { "sample_rate": 16000, "channels": 1 }
Server → Client  (text)   { "event": "handshake_ok", "session_id": "..." }
Client → Server  (binary) <float32 PCM frames — continuous stream>
Server → Client  (text)   { "is_deepfake": bool, "confidence_score": float, ... }
Client → Server  (text)   "STOP"
Server → Client  (text)   { "event": "session_end", "windows_analysed": N }
```

### Threat History Response
```json
{
  "total": 142,
  "skip": 0,
  "limit": 20,
  "logs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-04-13T18:00:00Z",
      "module_type": "intent",
      "risk_level": "SCAM_DETECTED",
      "details_json": { "is_scam": true, "scam_score": 91.0, "reason": "..." }
    }
  ]
}
```

---

## ⚡ Getting Started

### Prerequisites

| Requirement | Version | Notes |
|:------------|:-------:|:------|
| Python | 3.10+ | Backend runtime |
| PostgreSQL | 15+ | Must be running before `uvicorn` starts |
| Flutter | 3.19+ | Frontend only |

### 1 — Clone & enter the backend

```bash
git clone https://github.com/Anbu-Navin-Devs/Aegis-Scam-Firewall.git
cd Aegis-Scam-Firewall/backend
```

### 2 — Create a virtual environment

```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure environment variables

> ⚠️ **Both keys are required.** The server will refuse to start without them.

Create a `.env` file inside the `backend/` folder:

```env
# Google Gemini API — obtain at https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# PostgreSQL connection string — must use the postgresql+asyncpg:// scheme.
# Replace user, password, host, port, and database name to match your setup.
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aegis
```

> 💡 **Quick local DB setup:**
> ```bash
> # Create the database (run once)
> psql -U postgres -c "CREATE DATABASE aegis;"
> ```
> SQLAlchemy will create the `threat_logs` table automatically on first startup.

### 5 — Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On startup you will see:
```
INFO  Initialising database schema…
INFO  Database schema ready.
INFO  Uvicorn running on http://0.0.0.0:8000
```

### 6 — Explore the API

Open **http://localhost:8000/docs** for the full interactive Swagger UI.

---

### Frontend Setup

```bash
cd ../frontend
flutter pub get
flutter run
```

> Point the Flutter app's base URL to `http://<your-machine-ip>:8000` when running on a physical device.

---

## 🔐 Architecture Note — Async Threat Logging

All three detection modules log their results to PostgreSQL **without blocking the AI response path**:

- **REST endpoints** (`/analyze/intent`, `/document/scan`): use FastAPI's built-in `BackgroundTasks`. The HTTP response is sent to the Flutter client first; the database `INSERT` runs immediately afterward in the same async event loop.
- **WebSocket endpoint** (`/live-audio/stream`): uses `asyncio.create_task` to fire a database write coroutine concurrently with the next binary frame being received. WebSocket sessions are **never paused** by persistence work.

This guarantees that the scam-detection latency seen by the user is determined solely by the AI model — not by database I/O.

---

## 👥 Team

<div align="center">

<table>
<tr>
<td align="center" width="50%">

<a href="https://github.com/Anbu-2006">
<img src="https://github.com/Anbu-2006.png" width="120" style="border-radius:50%;" alt="Anbuselvan T"/>
</a>

### Anbuselvan T
**AI & Backend Engineer**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Anbu-2006)

`AI/LLM` `FastAPI` `SQLAlchemy` `PostgreSQL` `Python`

</td>
<td align="center" width="50%">

<a href="https://github.com/navin18-cmd">
<img src="https://github.com/navin18-cmd.png" width="120" style="border-radius:50%;" alt="Navin"/>
</a>

### Navin
**Frontend Developer**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/navin18-cmd)

`Flutter` `UI/UX` `State Management` `Dart`

</td>
</tr>
</table>

</div>

> This project structure is designed so both developers can **push and pull simultaneously** without merge conflicts, since `/backend` and `/frontend` are fully independent modules.

---

## 🤝 Contributing

1. Create a feature branch from `main`.
2. Work only within your designated folder (`/backend` or `/frontend`).
3. Write tests for new features.
4. Submit a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<br/>

<div align="center">

**Built with 🛡️ by [Anbuselvan T](https://github.com/Anbu-2006) & [Navin](https://github.com/navin18-cmd)**

*Because your first line of defense should be intelligent.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:050505,25:121212,50:1a1a1a,75:121212,100:050505&height=120&section=footer" width="100%"/>

</div>
