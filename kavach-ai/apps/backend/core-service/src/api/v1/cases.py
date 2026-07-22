from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.database.session import get_db
from src.schemas.core import CaseCreate, CaseUpdate, CaseResponse, PaginatedResponse
from src.services.case import case_service
from src.repositories.case import case_repo

router = APIRouter()

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    request: Request,
    data: CaseCreate,
    db: AsyncSession = Depends(get_db)
):
    # In a real app we'd pass req_id to service
    return await case_service.create_case(db, data)

@router.get("/{id}", response_model=CaseResponse)
async def get_case(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    case_obj = await case_service.get_case(db, id)
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case not found")
    return case_obj

@router.get("/", response_model=PaginatedResponse)
async def list_cases(
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    items, total = await case_repo.get_multi_paginated(
        db, skip=skip, limit=page_size, status=status
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

@router.patch("/{id}", response_model=CaseResponse)
async def update_case(
    request: Request,
    id: UUID,
    data: CaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await case_service.update_case(db, id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Case not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.headers.get("x-user-id", "system")
    deleted = await case_service.delete_case(db, id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
