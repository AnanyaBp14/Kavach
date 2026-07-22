from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid
from datetime import datetime, timezone
from src.repositories.complaint import complaint_repo
from src.repositories.threat import threat_repo
from src.schemas.core import ComplaintCreate, ComplaintUpdate, ThreatAssessmentCreate
from src.models.core import Complaint, ThreatAssessment

import structlog

logger = structlog.get_logger()

class ComplaintService:
    async def create_complaint(self, db: AsyncSession, data: ComplaintCreate, req_id: str = None, corr_id: str = None, user_id: str = None) -> Complaint:
        complaint_dict = data.model_dump()
        
        complaint_number = f"CMP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        complaint_dict['complaint_number'] = complaint_number
        
        complaint = await complaint_repo.create(db, obj_in=complaint_dict)
        
        # Publish event
        from src.producers.kafka_producer import kafka_producer
        from src.events.schemas import KafkaEvent
        
        event = KafkaEvent(
            event_type="complaint.created",
            request_id=req_id,
            correlation_id=corr_id,
            user_id=user_id,
            payload={"complaint_id": str(complaint.id), "status": complaint.status}
        )
        await kafka_producer.send_event("core-events", event)
        
        return complaint

    async def get_complaint(self, db: AsyncSession, id: UUID) -> Complaint | None:
        return await complaint_repo.get(db, id)

    async def update_complaint(self, db: AsyncSession, id: UUID, data: ComplaintUpdate, req_id: str = None, corr_id: str = None, user_id: str = None) -> Complaint | None:
        complaint = await complaint_repo.get(db, id)
        if not complaint:
            return None
        updated = await complaint_repo.update(db, db_obj=complaint, obj_in=data.model_dump(exclude_unset=True))
        
        from src.producers.kafka_producer import kafka_producer
        from src.events.schemas import KafkaEvent
        
        event = KafkaEvent(
            event_type="complaint.updated",
            request_id=req_id,
            correlation_id=corr_id,
            user_id=user_id,
            payload={"complaint_id": str(updated.id), "status": updated.status}
        )
        await kafka_producer.send_event("core-events", event)
        
        return updated

    async def delete_complaint(self, db: AsyncSession, id: UUID, user_id: str) -> Complaint | None:
        return await complaint_repo.soft_delete(db, id=id, deleted_by=user_id)

    async def assess_threat(self, db: AsyncSession, id: UUID, data: ThreatAssessmentCreate) -> ThreatAssessment | None:
        complaint = await complaint_repo.get(db, id)
        if not complaint:
            return None
            
        threat = await threat_repo.create(db, obj_in=data.model_dump())
        return threat

complaint_service = ComplaintService()
