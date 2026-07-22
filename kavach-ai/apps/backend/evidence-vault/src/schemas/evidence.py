from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List

class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EvidenceCreate(BaseModel):
    complaint_id: Optional[str] = None
    case_id: Optional[str] = None
    evidence_type: str
    title: str
    description: Optional[str] = None
    file_url: str
    bucket_name: str
    object_key: str
    sha256_hash: str
    mime_type: str
    file_size: int
    uploaded_by: str
    verification_status: str = "PENDING"

class EvidenceResponse(EvidenceCreate, TimestampSchema):
    id: UUID
    
class ChainOfCustodyCreate(BaseModel):
    evidence_id: UUID
    action: str
    actor: str
    previous_hash: Optional[str] = None
    current_hash: str
    notes: Optional[str] = None

class ChainOfCustodyResponse(ChainOfCustodyCreate, TimestampSchema):
    id: UUID

class EvidenceAccessLogCreate(BaseModel):
    evidence_id: UUID
    user_id: str
    action: str
    ip_address: Optional[str] = None

class DigitalSignatureCreate(BaseModel):
    evidence_id: UUID
    signature_algorithm: str
    signature_value: str
    certificate_metadata: Optional[str] = None

class DigitalSignatureResponse(DigitalSignatureCreate, TimestampSchema):
    id: UUID

class TimelineResponse(BaseModel):
    events: List[ChainOfCustodyResponse]
    access_logs: List[TimestampSchema] # Simplified
