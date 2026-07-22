import json
import os
from aiokafka import AIOKafkaProducer
from src.config.settings import settings
import structlog
from datetime import datetime, timezone
import uuid

logger = structlog.get_logger()

class KafkaProducerClient:
    def __init__(self):
        self.producer = None

    async def start(self):
        if os.environ.get("TESTING") == "1":
            return
            
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        await self.producer.start()
        logger.info("Kafka producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send_event(self, event_type: str, payload: dict, req_id: str = None, corr_id: str = None):
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": req_id,
            "correlation_id": corr_id,
            "payload": payload
        }
        
        if os.environ.get("TESTING") == "1":
            logger.info("TESTING MODE: Event mocked", event_type=event_type)
            return
            
        if not self.producer:
            logger.warning("Kafka producer not initialized")
            return
            
        await self.producer.send_and_wait("ai-events", event)
        logger.info("Event published", event_type=event_type)

kafka_producer = KafkaProducerClient()
