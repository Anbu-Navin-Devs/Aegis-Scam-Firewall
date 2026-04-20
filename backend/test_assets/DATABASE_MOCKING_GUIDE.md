# Aegis Database Setup & Mock Data Guide
## For Frontend (Navin) & Backend Developers

This guide provides a complete overview of the Aegis database structure and includes a plug-and-play Python script to seed your local database with realistic mock data. This allows the frontend to test the History Dashboard and pagination without needing to manually generate threats via the endpoints.

---

## 1. Database Schema

The Aegis backend uses **PostgreSQL**. All detected threats are stored in a single, highly flexible table called `threat_logs`.

### Table: `threat_logs`
| Column Name | Data Type | Description |
|---|---|---|
| `id` | `UUID` (Primary Key) | Unique identifier for the threat log. |
| `timestamp` | `TIMESTAMP` | UTC timestamp of when the threat was detected. |
| `module_type` | `VARCHAR` | The AI module that caught the threat: `'intent'`, `'audio'`, or `'document'`. |
| `risk_level` | `VARCHAR` | The severity of the threat (e.g., `'HIGH'`, `'CRITICAL'`, `'SCAM_DETECTED'`). |
| `details_json`| `JSONB` | **Crucial Field:** The entire raw JSON payload returned by the AI. This allows the schema to be flexible without needing new columns if the AI output changes. |

---

## 2. How the Data Looks (`details_json`)

Because `details_json` is a `JSONB` column, its internal structure depends on the `module_type`. Here is exactly what the frontend will receive in the `details_json` field when querying the `/history/logs` endpoint:

### A. Intent Module (`module_type: "intent"`)
```json
{
  "is_scam": true,
  "scam_score": 96,
  "reason": "High-pressure urgency tactics detected: mentions immediate payment, threatens legal action, impersonates authority figure (IRS)."
}
```

### B. Document Module (`module_type: "document"`)
```json
{
  "risk_level": "CRITICAL",
  "summary": "This contract contains a hidden auto-renewal and a mandatory arbitration waiver.",
  "flagged_clauses": [
    "Section 4.2: Auto-renewal clause hidden in fine print.",
    "Section 7.1: Mandatory binding arbitration waiver prevents class-action."
  ]
}
```

### C. Live Audio Module (`module_type: "audio"`)
```json
{
  "is_deepfake": true,
  "confidence_score": 88.5,
  "analysis_details": "Spectral flatness is abnormally uniform (0.92) suggesting synthesised speech. Pitch variability is very low."
}
```

---

## 3. Database Setup Instructions (Local)

If you haven't set up the database yet, follow these steps:

1. **Install PostgreSQL** on your machine.
2. Open your terminal or `psql` command line.
3. Run the following command to create the database:
   ```sql
   CREATE DATABASE aegis;
   ```
4. Update your `backend/.env` file:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aegis
   ```
   *(Change `postgres:postgres` to your actual PostgreSQL username and password).*
5. Start the backend (`uvicorn app.main:app`). **The backend will automatically create the `threat_logs` table on startup.**

---

## 4. Seeding the Database with Mock Data

Instead of manually hitting the APIs to generate data, you can run the provided `seed_mock_db.py` script. It will automatically inject 50 highly realistic threat logs directly into your PostgreSQL database.

### How to use the seeder:
1. Ensure your PostgreSQL database is running.
2. Ensure you are in the `backend/` directory and your virtual environment is active.
3. Run the script:
   ```bash
   python test_assets/seed_mock_db.py
   ```
4. You should see a success message. You can now test the Flutter History Dashboard by querying `GET /api/v1/history/logs?limit=20`!
