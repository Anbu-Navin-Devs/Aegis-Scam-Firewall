"""
Aegis: The Cognitive Scam Firewall — Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aegis API",
    description="AI-Powered Scam Detection & Defense API",
    version="0.1.0",
)

# CORS — allow the Flutter frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "online", "service": "Aegis Cognitive Scam Firewall"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "modules": {
            "deepfake_detection": "not_initialized",
            "intent_analysis": "not_initialized",
            "honeypot_defense": "not_initialized",
        },
    }

