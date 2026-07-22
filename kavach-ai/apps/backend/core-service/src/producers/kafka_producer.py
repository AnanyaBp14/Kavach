import json
from aiokafka import AIOKafkaProducer
from src.config.settings import settings
from src.events.schemas import KafkaEvent
import structlog

logger = structlog.get_logger()

class KafkaProducerClient:
    def __init__(self):
        self.producer = None

    async def start(self):
        import os
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

    async def send_event(self, topic: str, event: KafkaEvent):
        import os
        if os.environ.get("TESTING") == "1":
            logger.info("TESTING MODE: Event mocked", event_type=event.event_type, topic=topic)
            return
            
        if not self.producer:
            logger.warning("Kafka producer not initialized, skipping event", event_type=event.event_type)
            return
            
        await self.producer.send_and_wait(topic, event.model_dump())
        logger.info("Event published", event_type=event.event_type, topic=topic)

kafka_producer = KafkaProducerClient()
