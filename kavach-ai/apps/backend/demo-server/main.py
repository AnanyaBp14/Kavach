import asyncio
import json
import random
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, Query, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, get_db_connection
from agents.vision_agent import verify_banknote
from agents.fusion_agent import fuse_intelligence
from websocket.alerts import manager, background_alert_generator
from auth_jwt import authenticate_user

app = FastAPI(
    title="KAVACH AI Multi-Agent Intelligence Platform (Demo Engine)",
    version="2.0.0",
    description="Standalone zero-dependency backend supporting SQLite persistence, AI vision verification, fusion engine, audit trails, and WebSockets."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(background_alert_generator())

def load_json(filename: str):
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

start_time = time.time()

# ------------------------------------------------------------------
# Health & Status
# ------------------------------------------------------------------
@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "mode": "demo",
        "service": "KAVACH AI Multi-Agent Intelligence Platform",
        "database": "SQLite (Persisted)",
        "uptime_seconds": int(time.time() - start_time),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    result = authenticate_user(req.username, req.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result

# ------------------------------------------------------------------
# Counterfeit Vision Agent
# ------------------------------------------------------------------
@app.post("/api/v1/vision/verify-note")
async def verify_note(file: Optional[UploadFile] = File(None), note_type: str = Form("₹500")):
    image_bytes = b""
    filename = "currency_sample.jpg"
    if file:
        image_bytes = await file.read()
        filename = file.filename
    
    return verify_banknote(image_bytes, filename)

# ------------------------------------------------------------------
# Graph Intelligence Agent
# ------------------------------------------------------------------
@app.get("/api/v1/graph/network")
@app.get("/api/v1/graph/entity/{entity_id}")
def get_graph_network(entity_id: Optional[str] = "COMP-8924"):
    graph = load_json("graph.json")
    return {
        "root_entity_id": entity_id,
        "nodes": graph.get("nodes", []),
        "edges": graph.get("edges", []),
        "fraud_ring": "Fraud Ring Alpha (Jamtara UPI Fraud)",
        "mode": "demo"
    }

# ------------------------------------------------------------------
# Geospatial Agent
# ------------------------------------------------------------------
@app.get("/api/v1/geo/hotspots")
def get_geo_hotspots(format: Optional[str] = Query("json")):
    raw_hotspots = load_json("hotspots.json")
    if format == "geojson":
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [h["lon"], h["lat"]]},
                "properties": h
            }
            for h in raw_hotspots
        ]
        return {"type": "FeatureCollection", "features": features, "mode": "demo"}
    return raw_hotspots

@app.get("/api/v1/geo/districts")
def get_geo_districts():
    return load_json("districts.json")

# ------------------------------------------------------------------
# Multi-Agent Fusion Engine
# ------------------------------------------------------------------
class FuseRequest(BaseModel):
    complaint_text: str
    phone: Optional[str] = None
    evidence_filename: Optional[str] = None

@app.post("/api/v1/fuse-intel")
def fuse_intel(req: FuseRequest):
    return fuse_intelligence(req.complaint_text, req.phone, req.evidence_filename)

# ------------------------------------------------------------------
# Human Review Queue
# ------------------------------------------------------------------
class ReviewRequest(BaseModel):
    complaint_id: str
    risk_score: int
    notes: Optional[str] = "High-risk alert flagged for officer review"

@app.post("/api/v1/reviews")
def create_review(req: ReviewRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    review_id = f"REV-{random.randint(100, 999)}"
    cursor.execute(
        "INSERT INTO reviews (id, complaint_id, risk_score, status, assigned_to) VALUES (?, ?, ?, ?, ?)",
        (review_id, req.complaint_id, req.risk_score, "PENDING_REVIEW", "Cyber Cell Officer")
    )
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "review_id": review_id, "message": "Ticket created in SQLite database"}

@app.get("/api/v1/reviews")
def list_reviews():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"reviews": rows}

# ------------------------------------------------------------------
# Audit Trail Log Endpoint
# ------------------------------------------------------------------
@app.get("/api/v1/audit/logs")
def get_audit_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 20")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"audit_logs": rows}

# ------------------------------------------------------------------
# Core KPIs & Demo Scenarios
# ------------------------------------------------------------------
@app.get("/kpis")
@app.get("/api/v1/core/kpis")
def get_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    complaints_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM assessments")
    assessments_count = cursor.fetchone()[0]
    conn.close()

    return {
        "activeComplaints": complaints_count,
        "activeIncidents": 89,
        "openCases": 34,
        "highRiskDistricts": 12,
        "activeFraudRings": 8,
        "threatAlerts": 15,
        "evidenceUploadedToday": 340,
        "aiAnalysesCompleted": assessments_count + 1102,
        "mode": "demo"
    }

@app.get("/api/v1/demo/scenarios/{scenario_id}")
def trigger_scenario(scenario_id: str):
    if scenario_id == "1": # Low Risk Bank Alert
        return fuse_intelligence("Routine SMS alert received from HDFC bank confirming salary credit.", phone="+91 91234 56789")
    elif scenario_id == "2": # Medium Risk Investment Scam
        return fuse_intelligence("Telegram user offered guaranteed 300% returns by completing online YouTube review tasks.", phone="+91 99887 76655")
    elif scenario_id == "3": # Critical Digital Arrest Scam
        return fuse_intelligence("Fake police officer claimed illegal customs contraband package seized in Mumbai. Coerced transfer of 50000 to HDFC #449281.", phone="+91 98765 43210")
    else:
        return {"error": "Invalid scenario ID"}

# ------------------------------------------------------------------
# WebSocket Alerts Endpoint
# ------------------------------------------------------------------
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
