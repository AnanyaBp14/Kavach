from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.core import Complaint
from src.repositories.base import CRUDBase
from typing import List, Tuple

class CRUDComplaint(CRUDBase[Complaint]):
    async def get_by_complaint_number(self, db: AsyncSession, complaint_number: str) -> Complaint | None:
        result = await db.execute(select(Complaint).filter(Complaint.complaint_number == complaint_number))
        return result.scalars().first()
        
    async def get_multi_paginated(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100,
        district: str | None = None, category: str | None = None, status: str | None = None
    ) -> Tuple[List[Complaint], int]:
        
        query = select(Complaint).filter(Complaint.deleted_at.is_(None))
        
        if district:
            query = query.filter(Complaint.district == district)
        if category:
            query = query.filter(Complaint.category == category)
        if status:
            query = query.filter(Complaint.status == status)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        
        return list(result.scalars().all()), total or 0

complaint_repo = CRUDComplaint(Complaint)
