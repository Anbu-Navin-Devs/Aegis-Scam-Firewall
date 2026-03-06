<p align="center">
  <img src="docs/assets/aegis_logo_placeholder.png" alt="Aegis Logo" width="200"/>
</p>

<h1 align="center">🛡️ Aegis: The Cognitive Scam Firewall</h1>

<p align="center">
  <em>AI-Powered Real-Time Scam Detection &amp; Defense for the Modern Mobile User</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#project-structure">Project Structure</a> •
  <a href="#team">Team</a> •
  <a href="#license">License</a>
</p>

---

## 📌 Mission

**Aegis** is an intelligent, multi-layered scam firewall that leverages cutting-edge AI to protect users from evolving digital threats — including deepfake calls, social-engineering messages, and phishing attacks.

Built as a 2nd-year AI & Data Engineering capstone project, Aegis combines three core defense pillars:

| Pillar | Description |
|---|---|
| 🎭 **AI Deepfake Detection** | Real-time analysis of audio/video streams to identify AI-generated deepfake content using spectral and temporal feature extraction. |
| 🧠 **Intent Analysis Engine** | NLP-driven classification of incoming messages, calls, and links to determine malicious intent and confidence scores. |
| 🍯 **Honeypot Defense System** | Automated engagement with detected scammers using AI-generated responses to waste attacker resources and gather threat intelligence. |

---

## ✨ Features

- 🔍 **Real-time deepfake audio/video detection**
- 💬 **SMS & chat intent classification** (phishing, social engineering, spam)
- 📞 **Call screening with live risk scoring**
- 🍯 **Honeypot auto-responder** to engage and exhaust scammers
- 📊 **Threat dashboard** with analytics and reporting
- 🔔 **Push notifications** for high-risk alerts
- 🔒 **On-device inference** for privacy-sensitive operations

---

## 🏗️ Architecture

Aegis follows a **client-server architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│                  Flutter Mobile App              │
│         (Android / Material Design 3)            │
├─────────────────────────────────────────────────┤
│                    REST API                       │
├─────────────────────────────────────────────────┤
│              FastAPI Backend (Python)             │
│  ┌─────────────┬──────────────┬────────────────┐ │
│  │  Deepfake   │   Intent     │   Honeypot     │ │
│  │  Detection  │   Analysis   │   Defense      │ │
│  │  Module     │   Engine     │   System       │ │
│  └─────────────┴──────────────┴────────────────┘ │
├─────────────────────────────────────────────────┤
│          PostgreSQL  │  Redis  │  ML Models      │
└─────────────────────────────────────────────────┘
```

> Full architecture documentation: [`docs/System_Architecture.md`](docs/System_Architecture.md)

---

## 📂 Project Structure

```
Aegis-Scam-Firewall/
│
├── backend/                  # Python/FastAPI backend
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   ├── core/             # App config, security, dependencies
│   │   ├── models/           # Database & Pydantic models
│   │   ├── services/         # Business logic & AI modules
│   │   └── main.py           # FastAPI application entry point
│   ├── tests/                # Backend unit & integration tests
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # Backend-specific documentation
│
├── frontend/                 # Flutter/Android mobile app
│   ├── lib/
│   │   ├── models/           # Data models
│   │   ├── screens/          # UI screens
│   │   ├── services/         # API clients & business logic
│   │   ├── widgets/          # Reusable UI components
│   │   └── main.dart         # App entry point
│   ├── test/                 # Frontend widget & unit tests
│   ├── pubspec.yaml          # Flutter dependencies
│   └── README.md             # Frontend-specific documentation
│
├── docs/                     # Project documentation
│   └── System_Architecture.md
│
├── .gitignore                # Git ignore rules (Python + Flutter)
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version |
|---|---|
| Python | >= 3.10 |
| Flutter | >= 3.19 |
| Android Studio | Latest |
| PostgreSQL | >= 15 |
| Git | >= 2.40 |

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
flutter pub get
flutter run
```

---

## 👥 Team

| Role | Responsibility |
|---|---|
| **Backend Developer** | FastAPI services, AI/ML models, database, API design |
| **Frontend Developer** | Flutter UI/UX, Android integration, state management |

> This project structure is designed so both developers can **push and pull simultaneously** without merge conflicts, since `/backend` and `/frontend` are fully independent modules.

---

## 🤝 Contributing

1. Create a feature branch from `main`: `git checkout -b feature/your-feature`
2. Work only within your designated folder (`/backend` or `/frontend`)
3. Write tests for new features
4. Submit a Pull Request with a clear description

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Aegis</strong> — Because your first line of defense should be intelligent. 🛡️
</p>

