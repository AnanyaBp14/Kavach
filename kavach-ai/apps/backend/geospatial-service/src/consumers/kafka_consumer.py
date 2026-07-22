import json
import os
import asyncio
from aiokafka import AIOKafkaConsumer
from src.config.settings import settings
import structlog
import uuid
from datetime import datetime, timezone
from src.database.session import async_session_factory
from src.database.models import GeoIncident
from src.services.spatial_analytics import spatial_engine

logger = structlog.get_logger()

# Very basic fallback coordinates for districts
DISTRICT_CENTERS = {
    "Jamtara": (23.95, 86.8),
    "Mewat": (28.1, 77.0),
    "Bharatpur": (27.2, 77.5),
    "Mathura": (27.5, 77.6),
    "Mumbai": (19.07, 72.87)
}

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.running = False

    async def start(self):
        if os.environ.get("TESTING") == "1":
            return
            
        self.consumer = AIOKafkaConsumer(
            "core-events", "evidence-events", "ai-events",
            bootstrap_servers=settings.KAFKA_BROKER,
            group_id="geospatial-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        await self.consumer.start()
        self.running = True
        logger.info("Geospatial Kafka consumer started")
        asyncio.create_task(self._consume_loop())

    async def stop(self):
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def _consume_loop(self):
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                event = msg.value
                event_type = event.get("event_type")
                if event_type in ["complaint.created", "incident.created", "threat.fused"]:
                    await self.process_event(event.get("payload", {}))
        except Exception as e:
            logger.error("Geo Consumer loop failed", error=str(e))

    async def process_event(self, payload: dict):
        district = payload.get("district", "Unknown")
        lat = payload.get("coordinates", {}).get("lat")
        lon = payload.get("coordinates", {}).get("lon")
        
        # Fallback to district center
        if not lat or not lon:
            center = DISTRICT_CENTERS.get(district, (20.5937, 78.9629)) # India center fallback
            lat, lon = center
            
        async with async_session_factory() as session:
            incident = GeoIncident(
                id=str(uuid.uuid4()),
                complaint_id=payload.get("id") or payload.get("complaint_id", "unknown"),
                lat=lat,
                lon=lon,
                location=f"POINT({lon} {lat})", # PostGIS Geometry WKT
                district=district,
                state=payload.get("state", "Unknown"),
                threat_score=payload.get("threat_score", 0.5),
                category=payload.get("category", "General")
            )
            session.add(incident)
            await session.commit()
            
        # Fire and forget clustering update for this district
        asyncio.create_task(spatial_engine.recompute_district_hotspots(district))

kafka_consumer = KafkaConsumerService()
