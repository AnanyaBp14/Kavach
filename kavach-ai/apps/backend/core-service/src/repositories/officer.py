from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.core import Officer
from src.repositories.base import CRUDBase
from typing import List, Tuple

class CRUDOfficer(CRUDBase[Officer]):
    async def get_multi_paginated(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100,
        district: str | None = None, available_only: bool = False
    ) -> Tuple[List[Officer], int]:
        
        query = select(Officer).filter(Officer.deleted_at.is_(None))
        
        if district:
            query = query.filter(Officer.district == district)
        if available_only:
            query = query.filter(Officer.availability == True)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        
        return list(result.scalars().all()), total or 0

officer_repo = CRUDOfficer(Officer)
