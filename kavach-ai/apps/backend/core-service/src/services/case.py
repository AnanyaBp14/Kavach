from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.repositories.case import case_repo
from src.schemas.core import CaseCreate, CaseUpdate
from src.models.core import Case

class CaseService:
    async def create_case(self, db: AsyncSession, data: CaseCreate) -> Case:
        return await case_repo.create(db, obj_in=data.model_dump())

    async def get_case(self, db: AsyncSession, id: UUID) -> Case | None:
        return await case_repo.get(db, id)

    async def update_case(self, db: AsyncSession, id: UUID, data: CaseUpdate) -> Case | None:
        case = await case_repo.get(db, id)
        if not case:
            return None
        return await case_repo.update(db, db_obj=case, obj_in=data.model_dump(exclude_unset=True))

    async def delete_case(self, db: AsyncSession, id: UUID, user_id: str) -> Case | None:
        return await case_repo.soft_delete(db, id=id, deleted_by=user_id)

case_service = CaseService()
