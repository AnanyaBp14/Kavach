from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from src.models.core import ComplaintCategory, ComplaintStatus, Priority, ThreatLevel

# Mixins
class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Complaint Schemas
class ComplaintCreate(BaseModel):
    citizen_id: str
    category: ComplaintCategory
    source: str
    description: str
    latitude: float = Field(..., ge=6.7, le=35.5) # India bounds approx
    longitude: float = Field(..., ge=68.1, le=97.4)
    district: str
    state: str

class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    priority: Optional[Priority] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)

class ComplaintResponse(ComplaintCreate, TimestampSchema):
    id: UUID
    complaint_number: str
    status: ComplaintStatus
    priority: Priority
    risk_score: float

# Threat Assessment Schemas
class ThreatAssessmentCreate(BaseModel):
    complaint_id: UUID
    threat_score: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    model_version: str
    ai_summary: str
    recommendation: str

class ThreatAssessmentResponse(ThreatAssessmentCreate, TimestampSchema):
    id: UUID

# Incident Schemas
class IncidentCreate(BaseModel):
    complaint_id: UUID
    threat_level: ThreatLevel
    current_status: str
    severity: str

class IncidentUpdate(BaseModel):
    threat_level: Optional[ThreatLevel] = None
    current_status: Optional[str] = None
    severity: Optional[str] = None

class IncidentResponse(IncidentCreate, TimestampSchema):
    id: UUID

# Officer Schemas
class OfficerCreate(BaseModel):
    user_id: str
    organization_id: str
    name: str
    rank: str
    district: str

class OfficerUpdate(BaseModel):
    availability: Optional[bool] = None
    active_cases: Optional[int] = None
    district: Optional[str] = None

class OfficerResponse(OfficerCreate, TimestampSchema):
    id: UUID
    availability: bool
    active_cases: int

# Case Schemas
class CaseCreate(BaseModel):
    incident_id: UUID
    investigation_status: str
    notes: Optional[str] = None

class CaseUpdate(BaseModel):
    investigation_status: Optional[str] = None
    notes: Optional[str] = None
    evidence_count: Optional[int] = None
    resolution: Optional[str] = None
    closed_at: Optional[datetime] = None

class CaseResponse(CaseCreate, TimestampSchema):
    id: UUID
    evidence_count: int
    resolution: Optional[str]
    closed_at: Optional[datetime]

# Assignment Schemas
class AssignmentCreate(BaseModel):
    officer_id: UUID
    case_id: UUID
    assigned_by: str
    status: str

class AssignmentResponse(AssignmentCreate, TimestampSchema):
    id: UUID

# Timeline Schemas
class TimelineEventCreate(BaseModel):
    case_id: UUID
    actor: str
    event_type: str
    message: str

class TimelineEventResponse(TimelineEventCreate, TimestampSchema):
    id: UUID

# Pagination Schemas
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
