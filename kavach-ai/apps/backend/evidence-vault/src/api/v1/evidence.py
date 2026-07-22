from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from src.database.session import get_db
from src.schemas.evidence import EvidenceResponse, TimelineResponse
from src.services.evidence import evidence_service
from src.repositories.evidence import evidence_repo, chain_repo, access_log_repo

router = APIRouter()

@router.post("/upload", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    request: Request,
    file: UploadFile = File(...),
    complaint_id: Optional[str] = Form(None),
    case_id: Optional[str] = Form(None),
    evidence_type: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    user_id = request.headers.get("x-user-id", "anonymous")
    
    return await evidence_service.upload_evidence(
        db, file, complaint_id, case_id, evidence_type, title, description, user_id, req_id, corr_id
    )

@router.get("/{id}", response_model=EvidenceResponse)
async def get_evidence(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    evidence = await evidence_repo.get(db, id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence

@router.get("/{id}/download")
async def get_download_url(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.headers.get("x-user-id", "anonymous")
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    
    url = await evidence_service.get_download_url(db, id, user_id, req_id, corr_id)
    return {"download_url": url}

@router.get("/{id}/timeline", response_model=TimelineResponse)
async def get_evidence_timeline(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    chain = await chain_repo.get_timeline(db, str(id))
    access_logs = await access_log_repo.get_logs(db, str(id))
    return TimelineResponse(events=chain, access_logs=access_logs)

@router.get("/{id}/verify")
async def verify_evidence(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    evidence = await evidence_repo.get(db, id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    user_id = request.headers.get("x-user-id", "anonymous")
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    
    await access_log_repo.create(db, obj_in={
        "evidence_id": id,
        "user_id": user_id,
        "action": "VERIFY"
    })
    
    from src.producers.kafka_producer import kafka_producer
    from src.events.schemas import KafkaEvent
    
    event = KafkaEvent(
        event_type="evidence.verified",
        request_id=req_id,
        correlation_id=corr_id,
        user_id=user_id,
        payload={"evidence_id": str(id), "status": evidence.verification_status}
    )
    await kafka_producer.send_event("evidence-events", event)
    
    return {"status": evidence.verification_status, "hash": evidence.sha256_hash}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    request: Request,
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.headers.get("x-user-id", "anonymous")
    req_id = request.headers.get("x-request-id")
    corr_id = request.headers.get("x-correlation-id")
    
    deleted = await evidence_repo.soft_delete(db, id=id, deleted_by=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    from src.producers.kafka_producer import kafka_producer
    from src.events.schemas import KafkaEvent
    
    event = KafkaEvent(
        event_type="evidence.deleted",
        request_id=req_id,
        correlation_id=corr_id,
        user_id=user_id,
        payload={"evidence_id": str(id)}
    )
    await kafka_producer.send_event("evidence-events", event)
