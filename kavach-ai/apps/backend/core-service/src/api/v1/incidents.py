from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.database.session import get_db
from src.schemas.core import IncidentCreate, IncidentUpdate, IncidentResponse, PaginatedResponse
from src.services.incident import incident_service
from src.repositories.incident import incident_repo

router = APIRouter()

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    request: Request,
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db)
):
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    user_id = request.headers.get("x-user-id")
    
    return await incident_service.create_incident(db, data, req_id, corr_id, user_id)

@router.get("/{id}", response_model=IncidentResponse)
async def get_incident(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    incident = await incident_service.get_incident(db, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/", response_model=PaginatedResponse)
async def list_incidents(
    page: int = 1,
    page_size: int = 10,
    threat_level: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    items, total = await incident_repo.get_multi_paginated(
        db, skip=skip, limit=page_size, threat_level=threat_level, severity=severity
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)

@router.patch("/{id}", response_model=IncidentResponse)
async def update_incident(
    request: Request,
    id: UUID,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db)
):
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    user_id = request.headers.get("x-user-id")
    
    updated = await incident_service.update_incident(db, id, data, req_id, corr_id, user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.headers.get("x-user-id", "system")
    deleted = await incident_service.delete_incident(db, id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")
