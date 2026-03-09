"""
Aegis: The Cognitive Scam Firewall — Backend API

Main application entry point with FastAPI initialization,
CORS configuration, and API version routing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from app.api.v1 import analyze
from app.api.v1 import deepfake

APP_TITLE = "Aegis Scam Firewall API"
APP_VERSION = "1.0.0"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    application = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        description="Core backend service for Aegis: The Cognitive Scam Firewall.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Development CORS policy: allows the local Flutter client to call the API.
    # ⚠️ TODO: In production, restrict allow_origins to specific domains only.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API v1 routers
    application.include_router(
        analyze.router,
        prefix="/api/v1"
    )
    application.include_router(
        deepfake.router,
        prefix="/api/v1"
    )

    @application.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        """Simple liveness endpoint used by clients and deployment checks."""
        return {
            "status": "Aegis Backend is Active",
            "version": APP_VERSION,
        }

    return application


app = create_app()
