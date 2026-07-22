from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.repositories.officer import officer_repo
from src.schemas.core import OfficerCreate, OfficerUpdate
from src.models.core import Officer

class OfficerService:
    async def create_officer(self, db: AsyncSession, data: OfficerCreate) -> Officer:
        return await officer_repo.create(db, obj_in=data.model_dump())

    async def get_officer(self, db: AsyncSession, id: UUID) -> Officer | None:
        return await officer_repo.get(db, id)

    async def update_officer(self, db: AsyncSession, id: UUID, data: OfficerUpdate) -> Officer | None:
        officer = await officer_repo.get(db, id)
        if not officer:
            return None
        return await officer_repo.update(db, db_obj=officer, obj_in=data.model_dump(exclude_unset=True))

    async def delete_officer(self, db: AsyncSession, id: UUID, user_id: str) -> Officer | None:
        return await officer_repo.soft_delete(db, id=id, deleted_by=user_id)

officer_service = OfficerService()
