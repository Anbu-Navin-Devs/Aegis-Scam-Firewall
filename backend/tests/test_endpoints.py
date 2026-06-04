import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models.schemas import IntentResponse

client = TestClient(app)


def test_health_endpoint():
    """Verify that the basic liveness health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "Aegis Backend is Active",
        "version": "1.0.0"
    }


@patch("app.api.v1.analyze.analyze_transcript_intent", new_callable=AsyncMock)
def test_intent_endpoint_success(mock_analyze):
    """Verify intent endpoint works when the API key is not configured (bypass mode)."""
    # Force settings key to be empty to bypass check
    with patch.object(settings, "AEGIS_API_KEY", ""):
        # Mock the service response
        mock_analyze.return_value = IntentResponse(
            is_scam=True,
            scam_score=90,
            reason="Mocked detection: high pressure tactics detected."
        )
        
        payload = {"transcript": "Hello, pay me $5000 immediately."}
        response = client.post("/api/v1/analyze/intent", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_scam"] is True
        assert data["scam_score"] == 90
        assert "Mocked detection" in data["reason"]


def test_intent_endpoint_missing_body():
    """Verify that input validation handles empty transcripts with 400 Bad Request."""
    with patch.object(settings, "AEGIS_API_KEY", ""):
        payload = {"transcript": "   "}
        response = client.post("/api/v1/analyze/intent", json=payload)
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]


def test_security_middleware_unauthorized():
    """Verify client is unauthorized when AEGIS_API_KEY is set but client sends wrong/no header."""
    with patch.object(settings, "AEGIS_API_KEY", "super-secret-key"):
        payload = {"transcript": "Some text"}
        
        # Test missing header
        response = client.post("/api/v1/analyze/intent", json=payload)
        assert response.status_code == 401
        assert "missing API key" in response.json()["detail"]
        
        # Test wrong header value
        response = client.post(
            "/api/v1/analyze/intent", 
            json=payload,
            headers={"X-Aegis-API-Key": "wrong-key"}
        )
        assert response.status_code == 401
        assert "Invalid or missing" in response.json()["detail"]


@patch("app.api.v1.analyze.analyze_transcript_intent", new_callable=AsyncMock)
def test_security_middleware_authorized(mock_analyze):
    """Verify client is authorized when sending the correct X-Aegis-API-Key header."""
    key = "super-secret-key"
    with patch.object(settings, "AEGIS_API_KEY", key):
        mock_analyze.return_value = IntentResponse(
            is_scam=False,
            scam_score=10,
            reason="Mocked safe transcript."
        )
        
        payload = {"transcript": "Hello, how are you?"}
        response = client.post(
            "/api/v1/analyze/intent", 
            json=payload,
            headers={"X-Aegis-API-Key": key}
        )
        
        assert response.status_code == 200
        assert response.json()["is_scam"] is False


def test_history_endpoint_unauthorized():
    """Verify history logs route requires authorization when key is configured."""
    with patch.object(settings, "AEGIS_API_KEY", "secret"):
        response = client.get("/api/v1/history/logs")
        assert response.status_code == 401


@patch("app.api.v1.history.get_threat_logs", new_callable=AsyncMock)
@patch("app.api.v1.history.count_threat_logs", new_callable=AsyncMock)
def test_history_endpoint_authorized(mock_count, mock_get):
    """Verify history endpoint returns logs payload when authorized."""
    mock_get.return_value = []
    mock_count.return_value = 0
    
    with patch.object(settings, "AEGIS_API_KEY", ""):
        response = client.get("/api/v1/history/logs")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "logs" in data
        assert data["total"] == 0
        assert isinstance(data["logs"], list)
