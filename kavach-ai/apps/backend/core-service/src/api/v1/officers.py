from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.database.session import get_db
from src.schemas.core import OfficerCreate, OfficerUpdate, OfficerResponse, PaginatedResponse
from src.services.officer import officer_service
from src.repositories.officer import officer_repo

router = APIRouter()

@router.post("/", response_model=OfficerResponse, status_code=status.HTTP_201_CREATED)
async def create_officer(
    request: Request,
    data: OfficerCreate,
    db: AsyncSession = Depends(get_db)
):
    return await officer_service.create_officer(db, data)

@router.get("/{id}", response_model=OfficerResponse)
async def get_officer(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    officer = await officer_service.get_officer(db, id)
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    return officer

@router.get("/", response_model=PaginatedResponse)
async def list_officers(
    page: int = 1,
    page_size: int = 10,
    district: str | None = None,
    available_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    items, total = await officer_repo.get_multi_paginated(
        db, skip=skip, limit=page_size, district=district, available_only=available_only
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

@router.patch("/{id}", response_model=OfficerResponse)
async def update_officer(
    request: Request,
    id: UUID,
    data: OfficerUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await officer_service.update_officer(db, id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Officer not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_officer(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.headers.get("x-user-id", "system")
    deleted = await officer_service.delete_officer(db, id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Officer not found")
