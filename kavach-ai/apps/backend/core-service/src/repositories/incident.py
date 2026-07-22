from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.core import Incident
from src.repositories.base import CRUDBase
from typing import List, Tuple

class CRUDIncident(CRUDBase[Incident]):
    async def get_multi_paginated(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100,
        threat_level: str | None = None, severity: str | None = None
    ) -> Tuple[List[Incident], int]:
        
        query = select(Incident).filter(Incident.deleted_at.is_(None))
        
        if threat_level:
            query = query.filter(Incident.threat_level == threat_level)
        if severity:
            query = query.filter(Incident.severity == severity)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        
        return list(result.scalars().all()), total or 0

incident_repo = CRUDIncident(Incident)
