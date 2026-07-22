import uuid
from typing import List
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, ForeignKey, Enum as SQLEnum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

# Enums
class ComplaintCategory(str, enum.Enum):
    SUPPORT = "Support"
    DIGITAL_ARREST = "Digital Arrest"
    UPI_FRAUD = "UPI Fraud"
    COUNTERFEIT_CURRENCY = "Counterfeit Currency"
    FAKE_CALL = "Fake Call"
    FAKE_SMS = "Fake SMS"
    DEEPFAKE_VOICE = "Deepfake Voice"
    MONEY_MULE = "Money Mule"
    IDENTITY_THEFT = "Identity Theft"
    PHISHING = "Phishing"
    FAKE_QR = "Fake QR"
    ATM_FRAUD = "ATM Fraud"

class ComplaintStatus(str, enum.Enum):
    PENDING = "Pending"
    INVESTIGATING = "Investigating"
    ESCALATED = "Escalated"
    CLOSED = "Closed"
    REJECTED = "Rejected"

class ThreatLevel(str, enum.Enum):
    GREEN = "Green"
    YELLOW = "Yellow"
    ORANGE = "Orange"
    RED = "Red"
    BLACK = "Black"

class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String, primary_key=True) # Matches Gateway schema UUID string
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    # This is a read-only reference for Core service

class Officer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "officers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True) # Linked to Gateway user
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String)
    rank: Mapped[str] = mapped_column(String)
    district: Mapped[str] = mapped_column(String)
    availability: Mapped[bool] = mapped_column(Boolean, default=True)
    active_cases: Mapped[int] = mapped_column(Integer, default=0)

    assignments = relationship("Assignment", back_populates="officer")

class Complaint(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "complaints"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    citizen_id: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[ComplaintCategory] = mapped_column(SQLEnum(ComplaintCategory))
    source: Mapped[str] = mapped_column(String)
    status: Mapped[ComplaintStatus] = mapped_column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING)
    priority: Mapped[Priority] = mapped_column(SQLEnum(Priority), default=Priority.MEDIUM)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    district: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String)

    threat_assessment = relationship("ThreatAssessment", back_populates="complaint", uselist=False)
    incident = relationship("Incident", back_populates="complaint", uselist=False)

class ThreatAssessment(Base, TimestampMixin):
    __tablename__ = "threat_assessments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True)
    threat_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String)
    ai_summary: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)

    complaint = relationship("Complaint", back_populates="threat_assessment")

class Incident(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "incidents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"))
    threat_level: Mapped[ThreatLevel] = mapped_column(SQLEnum(ThreatLevel))
    current_status: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)

    complaint = relationship("Complaint", back_populates="incident")
    case = relationship("Case", back_populates="incident", uselist=False)

class Case(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cases"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id"), unique=True)
    investigation_status: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)

    incident = relationship("Incident", back_populates="case")
    assignments = relationship("Assignment", back_populates="case")
    timeline_events = relationship("TimelineEvent", back_populates="case")

class Assignment(Base, TimestampMixin):
    __tablename__ = "assignments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    officer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("officers.id"))
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    assigned_by: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String) # e.g. "Active", "Reassigned", "Completed"

    officer = relationship("Officer", back_populates="assignments")
    case = relationship("Case", back_populates="assignments")

class TimelineEvent(Base, TimestampMixin):
    __tablename__ = "timeline_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    actor: Mapped[str] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)

    case = relationship("Case", back_populates="timeline_events")

class StatusHistory(Base, TimestampMixin):
    __tablename__ = "status_history"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String) # "Complaint", "Incident", "Case"
    entity_id: Mapped[str] = mapped_column(String)
    old_status: Mapped[str] = mapped_column(String)
    new_status: Mapped[str] = mapped_column(String)
    changed_by: Mapped[str] = mapped_column(String)
