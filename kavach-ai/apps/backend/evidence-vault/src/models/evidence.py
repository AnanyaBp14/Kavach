import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Text, Integer, ForeignKey
from src.models.base import Base, TimestampMixin, SoftDeleteMixin

class Evidence(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[str] = mapped_column(String, nullable=True) # UUID string or number
    case_id: Mapped[str] = mapped_column(String, nullable=True)
    evidence_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    bucket_name: Mapped[str] = mapped_column(String, nullable=False)
    object_key: Mapped[str] = mapped_column(String, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String, index=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    uploaded_by: Mapped[str] = mapped_column(String, nullable=False)
    verification_status: Mapped[str] = mapped_column(String, default="PENDING")

class ChainOfCustody(Base, TimestampMixin):
    __tablename__ = "chain_of_custody"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evidence.id"))
    action: Mapped[str] = mapped_column(String, nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    previous_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    current_hash: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class EvidenceAccessLog(Base, TimestampMixin):
    __tablename__ = "evidence_access_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evidence.id"))
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False) # View, Download, Verify
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)

class DigitalSignature(Base, TimestampMixin):
    __tablename__ = "digital_signature"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evidence.id"))
    signature_algorithm: Mapped[str] = mapped_column(String, nullable=False)
    signature_value: Mapped[str] = mapped_column(Text, nullable=False)
    certificate_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
