import pytest
from fastapi.testclient import TestClient
from src.main import app
import os
import json

# Ensure we're in testing mode
os.environ["TESTING"] = "1"

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

def test_liveness_check():
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "LIVE"}

def test_trigger_analysis_mocked():
    payload = {
        "complaint_id": "COMP-1234",
        "text_content": "I received a call from CBI saying my Aadhaar is linked to money laundering.",
        "metadata": {
            "phone": "9876543210",
            "district": "Jamtara",
            "analyze_currency": False
        }
    }
    
    response = client.post("/api/v1/ai/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert data["overall_threat"] == "HIGH"
    assert data["investigation_summary"] == "Mock summary"
    
    # Check timeline events
    timeline = data["timeline"]
    assert len(timeline) > 0
    steps = [event["step"] for event in timeline]
    assert "Scam Detection" in steps
    assert "Graph Analysis" in steps
    assert "Geo Analysis" in steps
    assert "Threat Fusion" in steps
    assert "Officer Recommendation" in steps
    
    # Check that model version and prompt versions are set
    assert data["model_version"] == "llama-3.3-70b-versatile"
    assert data["workflow_version"] == "v1"
    assert data["prompt_version"] == "v1"
