import pytest
from fastapi.testclient import TestClient
from src.main import app
import os

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

def test_get_hotspots_json_mocked():
    response = client.get("/api/v1/geo/hotspots?format=json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "H1"
    assert data[0]["district"] == "Jamtara"

def test_get_hotspots_geojson_mocked():
    response = client.get("/api/v1/geo/hotspots?format=geojson")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0
    feature = data["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert feature["properties"]["district"] == "Jamtara"

def test_get_districts_mocked():
    response = client.get("/api/v1/geo/districts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["district"] == "Jamtara"
    assert data[0]["risk_level"] == 95

def test_get_heatmap_mocked():
    response = client.get("/api/v1/geo/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["intensity"] == 0.9
