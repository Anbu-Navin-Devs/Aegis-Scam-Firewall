import asyncio
import json
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Import the database config and models from your app
from app.core.config import settings
from app.models.db_models import ThreatLog, Base

# Realistic mock payloads for the 3 different AI modules
MOCK_INTENT_LOGS = [
    {
        "risk_level": "SCAM_DETECTED",
        "details": {
            "is_scam": True,
            "scam_score": 96,
            "reason": "IRS Impersonation: Caller demanded immediate payment via gift cards and threatened arrest within 24 hours."
        }
    },
    {
        "risk_level": "SUSPICIOUS",
        "details": {
            "is_scam": True,
            "scam_score": 72,
            "reason": "Phishing Attempt: SMS claiming a package delivery failed and requires a small $2 payment via a shortened link."
        }
    }
]

MOCK_DOCUMENT_LOGS = [
    {
        "risk_level": "CRITICAL",
        "details": {
            "risk_level": "CRITICAL",
            "summary": "Contract contains extremely one-sided terms including a 150% early termination fee.",
            "flagged_clauses": [
                "Section 8: User agrees to pay 150% of remaining balance upon termination.",
                "Section 12: Company may sell all telemetry data to unlisted third parties."
            ]
        }
    },
    {
        "risk_level": "HIGH",
        "details": {
            "risk_level": "HIGH",
            "summary": "Standard lease agreement but contains a hidden auto-renewal clause.",
            "flagged_clauses": [
                "Section 4: Lease renews automatically for 12 months unless cancelled 90 days prior."
            ]
        }
    }
]

MOCK_AUDIO_LOGS = [
    {
        "risk_level": "DEEPFAKE_DETECTED",
        "details": {
            "is_deepfake": True,
            "confidence_score": 92.4,
            "analysis_details": "Unnatural pitch stability (std=2.1 Hz) and uniform spectral flatness typical of neural vocoders."
        }
    },
    {
        "risk_level": "SUSPICIOUS_AUDIO",
        "details": {
            "is_deepfake": True,
            "confidence_score": 76.8,
            "analysis_details": "Zero-crossing rate lacks natural human breathing pauses; cadence is strictly metronomic."
        }
    }
]

async def seed_database(num_records: int = 50):
    print(f"🔄 Connecting to {settings.DATABASE_URL}...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print(f"✅ Schema verified. Generating {num_records} mock logs...")
    
    async with async_session() as session:
        # Clear existing logs for a fresh start (optional, but good for testing)
        await session.execute(text("TRUNCATE TABLE threat_logs RESTART IDENTITY;"))
        
        now = datetime.utcnow()
        logs_to_insert = []
        
        for i in range(num_records):
            # Randomly pick a module type
            module_type = random.choice(["intent", "document", "audio"])
            
            if module_type == "intent":
                mock_data = random.choice(MOCK_INTENT_LOGS)
            elif module_type == "document":
                mock_data = random.choice(MOCK_DOCUMENT_LOGS)
            else:
                mock_data = random.choice(MOCK_AUDIO_LOGS)
            
            # Spread timestamps over the last 14 days
            random_minutes_ago = random.randint(1, 14 * 24 * 60)
            mock_time = now - timedelta(minutes=random_minutes_ago)
            
            log = ThreatLog(
                id=uuid.uuid4(),
                timestamp=mock_time,
                module_type=module_type,
                risk_level=mock_data["risk_level"],
                details_json=mock_data["details"]
            )
            logs_to_insert.append(log)
            
        # Bulk save
        session.add_all(logs_to_insert)
        await session.commit()
        
    print(f"🎉 Success! Inserted {num_records} highly realistic threat logs into the database.")
    print("👉 Navin: You can now test the Flutter Dashboard pagination using the GET /api/v1/history/logs endpoint!")
    
    await engine.dispose()

if __name__ == "__main__":
    # Ensure this script is run on Windows safely
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(seed_database(num_records=50))
