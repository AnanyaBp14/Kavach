import hashlib
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from src.repositories.evidence import evidence_repo, chain_repo, access_log_repo, signature_repo
from src.schemas.evidence import EvidenceCreate, ChainOfCustodyCreate, DigitalSignatureCreate
from src.models.evidence import Evidence, ChainOfCustody
from src.services.storage import storage_service
from src.producers.kafka_producer import kafka_producer
from src.events.schemas import KafkaEvent

import structlog

logger = structlog.get_logger()

class EvidenceService:
    async def upload_evidence(
        self, db: AsyncSession, file: UploadFile, complaint_id: str, case_id: str, 
        evidence_type: str, title: str, description: str, uploaded_by: str,
        req_id: str = None, corr_id: str = None
    ) -> Evidence:
        
        # Validation
        file_size = 0
        content = await file.read()
        file_size = len(content)
        if file_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 100MB.")
            
        # Hash generation
        sha256_hash = hashlib.sha256(content).hexdigest()
        
        # Duplicate detection
        existing = await evidence_repo.get_by_hash(db, sha256_hash)
        if existing:
            raise HTTPException(status_code=409, detail="Duplicate evidence detected via hash.")
            
        # Upload to MinIO
        object_key = f"{uuid.uuid4()}/{file.filename}"
        
        if os.environ.get("TESTING") != "1":
            file.file.seek(0)
            storage_service.upload_file(object_key, file.file, file_size, file.content_type)
            
        file_url = f"{storage_service.bucket}/{object_key}"

        evidence_data = EvidenceCreate(
            complaint_id=complaint_id,
            case_id=case_id,
            evidence_type=evidence_type,
            title=title,
            description=description,
            file_url=file_url,
            bucket_name=storage_service.bucket,
            object_key=object_key,
            sha256_hash=sha256_hash,
            mime_type=file.content_type,
            file_size=file_size,
            uploaded_by=uploaded_by,
            verification_status="VERIFIED"
        )
        
        evidence = await evidence_repo.create(db, obj_in=evidence_data.model_dump())
        
        # Initialize Chain of Custody
        chain_data = ChainOfCustodyCreate(
            evidence_id=evidence.id,
            action="UPLOADED",
            actor=uploaded_by,
            current_hash=sha256_hash,
            notes="Initial evidence upload"
        )
        await chain_repo.create(db, obj_in=chain_data.model_dump())
        
        # Mock Digital Signature (for hackathon purposes)
        signature_data = DigitalSignatureCreate(
            evidence_id=evidence.id,
            signature_algorithm="RSA-SHA256-MOCK",
            signature_value=hashlib.sha256((sha256_hash + "mock_private_key").encode()).hexdigest(),
            certificate_metadata="mock_cert_kavach_auth"
        )
        await signature_repo.create(db, obj_in=signature_data.model_dump())
        
        # Emit Kafka Event
        event = KafkaEvent(
            event_type="evidence.uploaded",
            request_id=req_id,
            correlation_id=corr_id,
            user_id=uploaded_by,
            payload={"evidence_id": str(evidence.id), "hash": sha256_hash}
        )
        await kafka_producer.send_event("evidence-events", event)
        
        return evidence

    async def get_download_url(self, db: AsyncSession, evidence_id: uuid.UUID, user_id: str, req_id: str = None, corr_id: str = None) -> str:
        evidence = await evidence_repo.get(db, evidence_id)
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
            
        # Record access log
        await access_log_repo.create(db, obj_in={
            "evidence_id": evidence_id,
            "user_id": user_id,
            "action": "DOWNLOAD"
        })
        
        # Emit Event
        event = KafkaEvent(
            event_type="evidence.accessed",
            request_id=req_id,
            correlation_id=corr_id,
            user_id=user_id,
            payload={"evidence_id": str(evidence.id), "action": "DOWNLOAD"}
        )
        await kafka_producer.send_event("evidence-events", event)
        
        if os.environ.get("TESTING") == "1":
            return f"http://mock-minio/download/{evidence.object_key}"
            
        url = storage_service.get_presigned_url(evidence.object_key)
        return url

evidence_service = EvidenceService()
