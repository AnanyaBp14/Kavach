from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.core import Case
from src.repositories.base import CRUDBase
from typing import List, Tuple

class CRUDCase(CRUDBase[Case]):
    async def get_multi_paginated(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100,
        status: str | None = None
    ) -> Tuple[List[Case], int]:
        
        query = select(Case).filter(Case.deleted_at.is_(None))
        
        if status:
            query = query.filter(Case.investigation_status == status)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        
        return list(result.scalars().all()), total or 0

case_repo = CRUDCase(Case)
