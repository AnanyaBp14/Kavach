import asyncio
import random
import time
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

async def background_alert_generator():
    """Simulates real-time public safety alerts broadcast over WebSocket."""
    alert_types = [
        {"severity": "Critical", "source": "Threat Fusion Engine", "msg": "Digital Arrest scam campaign detected targeting senior citizens in Mewat"},
        {"severity": "High", "source": "Fraud Network", "msg": "New 4-hop mule account cluster linked to HDFC Bank #449281"},
        {"severity": "Medium", "source": "Counterfeit Vision Agent", "msg": "Suspicious ₹500 note batch flagged at SBI ATM Jamtara Branch"},
        {"severity": "Critical", "source": "Geospatial Agent", "msg": "Hotspot alert: Phishing incident frequency +22% in Bharatpur"},
        {"severity": "Low", "source": "Evidence Vault", "msg": "SHA-256 chain of custody verified for Complaint #COMP-8924"}
    ]
    
    while True:
        await asyncio.sleep(8)
        if manager.active_connections:
            sample_alert = random.choice(alert_types).copy()
            sample_alert["timestamp"] = time.strftime("%H:%M:%S")
            sample_alert["id"] = int(time.time() * 1000)
            await manager.broadcast({"type": "NEW_ALERT", "alert": sample_alert})
