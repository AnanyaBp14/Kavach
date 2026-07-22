import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

def test_liveness_check():
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "LIVE"}
