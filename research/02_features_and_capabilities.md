# 02 — Features & Technical Capabilities

This document provides an exhaustive breakdown of the nine core modules and technical capabilities engineered into the Aegis Scam Firewall.

---

## 1. Autonomous Real-Time SMS Interceptor

*   **Implementation File:** [`SmsReceiver.kt`](file:///e:/Aegis-Scam-Firewall/frontend/app/src/main/java/com/aegis/scamfirewall/features/sms/SmsReceiver.kt)
*   **Operating Mechanism:**
    *   Listens for system broadcast `android.provider.Telephony.SMS_RECEIVED` with priority `999`.
    *   Reassembles multi-part PDU segments into complete text bodies using `Telephony.Sms.Intents.getMessagesFromIntent(intent)`.
    *   Executes asynchronous analysis using Kotlin Coroutines (`goAsync()` + `Dispatchers.IO`).
    *   Evaluates message text against the **Tier-1 Local ML Classifier** in **< 2 milliseconds**.
    *   If score $\ge 50$, immediately triggers high-priority Heads-Up Notification before the user opens their SMS app.
    *   Concurrently queries the cloud cognitive model for deep explanation and saves to the database if network connectivity is available.

---

## 2. Real-Time Call Voice Guardian (Deepfake Monitor)

*   **Implementation Files:**
    *   [`CallStateReceiver.kt`](file:///e:/Aegis-Scam-Firewall/frontend/app/src/main/java/com/aegis/scamfirewall/features/call/CallStateReceiver.kt)
    *   [`CallMonitorForegroundService.kt`](file:///e:/Aegis-Scam-Firewall/frontend/app/src/main/java/com/aegis/scamfirewall/core/service/CallMonitorForegroundService.kt)
*   **Operating Mechanism:**
    *   Detects telephony transitions via `TelephonyManager.ACTION_PHONE_STATE_CHANGED`.
    *   On `EXTRA_STATE_OFFHOOK` (call answered or dialed), automatically initiates `CallMonitorForegroundService` with `FOREGROUND_SERVICE_TYPE_MICROPHONE`.
    *   Activates `AudioRecord` configured for 16,000 Hz, 16-bit Mono PCM.
    *   Streams normalized float32 audio chunks over low-latency WebSocket (`/ws/live-audio`).
    *   Listens to incoming verdict flows: if synthetic voice confidence $\ge 50\%$, triggers `AegisNotificationManager.notifyDeepfakeCallDetected(...)` with an intelligent 10-second alert cooldown.
    *   On `EXTRA_STATE_IDLE` (call termination), stops audio capture, disconnects WebSocket, and cleanly terminates the foreground service.

---

## 3. High-Speed Tier-1 On-Device ML Classifier

*   **Implementation File:** [`LocalScamClassifier.kt`](file:///e:/Aegis-Scam-Firewall/frontend/app/src/main/java/com/aegis/scamfirewall/core/ml/LocalScamClassifier.kt)
*   **Operating Mechanism:**
    *   Zero-latency (<2ms), 100% offline, privacy-preserving classification.
    *   Evaluates against multi-vector social engineering signatures:
        1.  *Obfuscated Phishing Links*: Raw IP URLs (`http://192.168...`), URL shorteners (`bit.ly`, `tinyurl`, `cutt.ly`), fake subdomain traps (`secure-login`, `verify-account`), and high-risk TLDs (`.xyz`, `.icu`, `.buzz`, `.top`).
        2.  *High-Pressure Urgency*: "immediate action required", "within 24 hours", "account suspended", "arrest warrant".
        3.  *Authority Impersonation*: IRS, Social Security Administration, Bank of America, Chase, Wells Fargo, PayPal, USPS, FedEx, DHL, Netflix, Amazon.
        4.  *Financial Extortion*: Gift cards, bitcoin/crypto wallets, wire transfers, unpaid toll violations.
        5.  *Credential Harvesting*: "one-time password", "otp code", "confirm your pin", "verify your ssn".
        6.  *Prize / Lottery Lures*: "congratulations you won", "lucky winner", "unclaimed inheritance".

---

## 4. Tier-2 Cognitive Cloud AI Engine (NVIDIA NIM)

*   **Implementation File:** [`nvidia_service.py`](file:///e:/Aegis-Scam-Firewall/backend/app/services/nvidia_service.py)
*   **Model:** Meta Llama 3.3 70B Instruct (hosted on NVIDIA NIM Cloud).
*   **Role:**
    *   Extracts deep contextual and psychological coercion tactics (scarcity, intimidation, authority bias).
    *   Handles edge-case zero-day conversational scams where no specific keywords are present.
    *   Generates structured, human-readable explanations of why the message is malicious.

---

## 5. Multimodal Threat Fusion Engine

*   **Implementation File:** [`analyze.py` (`POST /api/v1/analyze/fusion`)](file:///e:/Aegis-Scam-Firewall/backend/app/api/v1/analyze.py#L225)
*   **Operating Mechanism:**
    *   Fuses inputs: `transcript`, `voice_deepfake_confidence` (0.0 to 1.0), and `sender_or_caller`.
    *   Applies multimodal threat multiplier:
        *   If both voice deepfake ($\ge 50\%$) AND text extortion ($\ge 50\%$) are present $\rightarrow$ Composite Score boosted up to $100\%$ (`CRITICAL`).
        *   If voice deepfake $\ge 60\%$ alone $\rightarrow$ High-Risk Synthetic Impersonation (`HIGH`).
        *   If text smishing $\ge 60\%$ alone $\rightarrow$ Financial Phishing (`HIGH`/`MEDIUM`).

---

## 6. Victim Tactical Countermeasure Advisor

*   Delivers **live verbal defense scripts** to protect the victim in real-time:
    *   *Voice Impersonation:* "Ask a private challenge question only the real person would know (e.g. childhood pet name). Hang up and dial their saved phone number directly."
    *   *Banking Fraud:* "Banks NEVER ask for OTPs or passwords over the phone. Hang up and call the number printed on the back of your physical card."
    *   *Government Extortion:* "Federal agencies notify by certified mail, never by urgent phone demands or gift card payments."
    *   *Payment Demands:* "Gift cards and crypto transfers are 100% fraudulent. Terminate communication immediately."

---

## 7. Standardized 1-Tap Cybercrime Incident Report

*   Compiles structured, court-admissible forensic evidence formatted for immediate submission to:
    *   **FTC** (`reportfraud.ftc.gov`)
    *   **FBI Internet Crime Complaint Center (IC3)** (`ic3.gov`)
    *   **National Cyber Crime Reporting Portal** (`cybercrime.gov.in` / 1930)
*   **Included Telemetry:**
    *   UTC Timestamp
    *   Suspect Identifier (Caller ID / SMS Header)
    *   Threat Classification & Numerical Risk Score
    *   Acoustic Deepfake Probability (%)
    *   Raw Intercepted Text & Coercion Tactic Breakdown

---

## 8. Predatory Document & Contract Scanner

*   **Implementation File:** [`document.py`](file:///e:/Aegis-Scam-Firewall/backend/app/api/v1/document.py)
*   **Model:** Meta Llama 3.2 11B Vision Instruct.
*   **Operating Mechanism:**
    *   Accepts multi-page legal PDFs, loan forms, and employment agreements.
    *   Renders pages to high-resolution bitmaps via `PyMuPDF`.
    *   Scans visual legalese for predatory terms:
        *   Perpetual auto-renewal traps (e.g. 90-day cancellation windows).
        *   Binding mandatory arbitration waivers.
        *   Unilateral data-selling clauses.
        *   Excessive liquidated early termination damages.
    *   Returns structured severity rating (`SAFE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), flagged clauses, and an executive summary.

---

## 9. Forensic Threat History Timeline

*   **Implementation Files:**
    *   [`HistoryScreen.kt`](file:///e:/Aegis-Scam-Firewall/frontend/app/src/main/java/com/aegis/scamfirewall/features/history/HistoryScreen.kt)
    *   [`history.py`](file:///e:/Aegis-Scam-Firewall/backend/app/api/v1/history.py)
*   **Operating Mechanism:**
    *   Maintains an asynchronous PostgreSQL audit log of all intercepted threats.
    *   Enables users to review past threats, view full forensic breakdowns, and export historical evidence.
