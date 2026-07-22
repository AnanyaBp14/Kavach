from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from src.database.session import get_db
from src.schemas.core import ComplaintCreate, ComplaintUpdate, ComplaintResponse, PaginatedResponse
from src.services.complaint import complaint_service
from src.repositories.complaint import complaint_repo

router = APIRouter()

@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    request: Request,
    data: ComplaintCreate,
    db: AsyncSession = Depends(get_db)
):
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    user_id = request.headers.get("x-user-id")
    
    return await complaint_service.create_complaint(db, data, req_id, corr_id, user_id)

@router.get("/{id}", response_model=ComplaintResponse)
async def get_complaint(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    complaint = await complaint_service.get_complaint(db, id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.get("/", response_model=PaginatedResponse)
async def list_complaints(
    page: int = 1,
    page_size: int = 10,
    district: str | None = None,
    category: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    items, total = await complaint_repo.get_multi_paginated(
        db, skip=skip, limit=page_size, district=district, category=category, status=status
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

@router.patch("/{id}", response_model=ComplaintResponse)
async def update_complaint(
    request: Request,
    id: UUID,
    data: ComplaintUpdate,
    db: AsyncSession = Depends(get_db)
):
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    user_id = request.headers.get("x-user-id")
    
    updated = await complaint_service.update_complaint(db, id, data, req_id, corr_id, user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.headers.get("x-user-id", "system")
    deleted = await complaint_service.delete_complaint(db, id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Complaint not found")
