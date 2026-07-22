from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.repositories.incident import incident_repo
from src.schemas.core import IncidentCreate, IncidentUpdate
from src.models.core import Incident

class IncidentService:
    async def create_incident(self, db: AsyncSession, data: IncidentCreate, req_id: str = None, corr_id: str = None, user_id: str = None) -> Incident:
        incident = await incident_repo.create(db, obj_in=data.model_dump())
        
        from src.producers.kafka_producer import kafka_producer
        from src.events.schemas import KafkaEvent
        
        event = KafkaEvent(
            event_type="incident.created",
            request_id=req_id,
            correlation_id=corr_id,
            user_id=user_id,
            payload={"incident_id": str(incident.id), "threat_level": incident.threat_level}
        )
        await kafka_producer.send_event("core-events", event)
        return incident

    async def get_incident(self, db: AsyncSession, id: UUID) -> Incident | None:
        return await incident_repo.get(db, id)

    async def update_incident(self, db: AsyncSession, id: UUID, data: IncidentUpdate, req_id: str = None, corr_id: str = None, user_id: str = None) -> Incident | None:
        incident = await incident_repo.get(db, id)
        if not incident:
            return None
        return await incident_repo.update(db, db_obj=incident, obj_in=data.model_dump(exclude_unset=True))

    async def delete_incident(self, db: AsyncSession, id: UUID, user_id: str) -> Incident | None:
        return await incident_repo.soft_delete(db, id=id, deleted_by=user_id)

incident_service = IncidentService()
