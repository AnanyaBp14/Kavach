import json
import os
import asyncio
from aiokafka import AIOKafkaConsumer
from src.config.settings import settings
from src.database.neo4j_client import neo4j_client
import structlog
from datetime import datetime, timezone

logger = structlog.get_logger()

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
            group_id="fraud-network-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        await self.consumer.start()
        self.running = True
        logger.info("Fraud Network Kafka consumer started")
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
                logger.info("Received event for graph ingestion", event_type=event_type)
                await self.process_event(event_type, event.get("payload", {}), event)
        except Exception as e:
            logger.error("Consumer loop failed", error=str(e))

    async def process_event(self, event_type: str, payload: dict, full_event: dict):
        timestamp = full_event.get("timestamp", datetime.now(timezone.utc).isoformat())
        
        if event_type == "complaint.created" or event_type == "complaint.updated":
            await self._handle_complaint(payload, timestamp)
        elif event_type == "evidence.uploaded":
            await self._handle_evidence(payload, timestamp)
        elif event_type == "threat.fused":
            await self._handle_threat(payload, timestamp)
        elif event_type == "officer.assigned":
            await self._handle_officer(payload, timestamp)
        # Adding stubs for the other required events for idempotency
        elif event_type in ["incident.created", "case.created", "recommendation.generated"]:
            logger.info("Event mapped to generic graph update", event_type=event_type)

    async def _handle_complaint(self, payload: dict, timestamp: str):
        query = """
        MERGE (c:Complaint {id: $complaint_id})
        SET c.updated_at = $timestamp, c.source_event = 'complaint'
        
        WITH c
        UNWIND $phone_numbers AS phone
        MERGE (p:Phone {id: phone})
        MERGE (c)-[:REPORTED]->(p)
        
        WITH c
        UNWIND $upi_ids AS upi
        MERGE (u:UPI {id: upi})
        MERGE (c)-[:REPORTED]->(u)
        
        WITH c
        UNWIND $bank_accounts AS acc
        MERGE (a:BankAccount {id: acc})
        MERGE (c)-[:REPORTED]->(a)
        
        WITH c
        UNWIND $device_ids AS device
        MERGE (d:Device {id: device})
        MERGE (c)-[:REPORTED]->(d)
        """
        
        params = {
            "complaint_id": payload.get("id", "unknown"),
            "timestamp": timestamp,
            "phone_numbers": payload.get("phone_numbers", []),
            "upi_ids": payload.get("upi_ids", []),
            "bank_accounts": payload.get("bank_accounts", []),
            "device_ids": payload.get("device_ids", [])
        }
        await neo4j_client.execute_query(query, params)

    async def _handle_evidence(self, payload: dict, timestamp: str):
        query = """
        MERGE (c:Complaint {id: $complaint_id})
        MERGE (e:Evidence {id: $evidence_id})
        SET e.hash = $hash, e.updated_at = $timestamp
        MERGE (e)-[:LINKED_TO]->(c)
        """
        await neo4j_client.execute_query(query, {
            "complaint_id": payload.get("complaint_id", "unknown"),
            "evidence_id": payload.get("evidence_id", "unknown"),
            "hash": payload.get("hash", ""),
            "timestamp": timestamp
        })

    async def _handle_threat(self, payload: dict, timestamp: str):
        query = """
        MERGE (t:Threat {id: $session_id})
        SET t.score = $score, t.overall_threat = $overall_threat, t.updated_at = $timestamp
        """
        await neo4j_client.execute_query(query, {
            "session_id": payload.get("session_id", "unknown"),
            "score": payload.get("score", 0),
            "overall_threat": payload.get("overall_threat", "UNKNOWN"),
            "timestamp": timestamp
        })

    async def _handle_officer(self, payload: dict, timestamp: str):
        query = """
        MERGE (o:Officer {id: $officer_id})
        MERGE (c:Complaint {id: $complaint_id})
        MERGE (o)-[:ASSIGNED_TO]->(c)
        SET o.updated_at = $timestamp
        """
        await neo4j_client.execute_query(query, {
            "officer_id": payload.get("officer_id", "unknown"),
            "complaint_id": payload.get("complaint_id", "unknown"),
            "timestamp": timestamp
        })

kafka_consumer = KafkaConsumerService()
