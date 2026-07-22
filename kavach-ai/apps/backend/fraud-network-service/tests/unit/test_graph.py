import pytest
from fastapi.testclient import TestClient
from src.main import app
import os
import asyncio

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

def test_get_case_graph_mocked():
    response = client.get("/api/v1/graph/case/COMP-1234")
    assert response.status_code == 200
    data = response.json()
    
    assert "nodes" in data
    assert "edges" in data
    assert "risk_profile" in data
    assert data["ring_size"] == 2
    assert data["risk_profile"]["overall_risk"] == 90
    assert data["nodes"][0]["id"] == "C1"
    assert data["edges"][0]["source"] == "C1"
    assert data["edges"][0]["target"] == "P1"

def test_get_neighbors_mocked():
    response = client.get("/api/v1/graph/neighbors/P1")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data

def test_expand_graph_mocked():
    response = client.post("/api/v1/graph/expand", json=["P1", "C1"])
    assert response.status_code == 200
    data = response.json()
    assert data["ring_size"] == 2

def test_expand_graph_empty_mocked():
    response = client.post("/api/v1/graph/expand", json=[])
    assert response.status_code == 400
