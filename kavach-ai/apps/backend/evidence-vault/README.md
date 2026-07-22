# KAVACH AI - Evidence Vault Service

The Evidence Vault Service handles the secure storage, verification, and auditability of all evidentiary files for KAVACH AI.

## Architecture
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy 2.0 Async, Alembic)
- **Object Storage**: MinIO (S3 Compatible)
- **Event Streaming**: Kafka (KRaft mode) via `aiokafka`
- **Caching**: Redis
- **Logging**: Structlog (JSON)
- **Validation**: Pydantic v2

## Features
- Strict SHA-256 validation before upload for deduplication and integrity.
- MinIO integration for secure file storage and presigned download URLs.
- Immutable `ChainOfCustody` records for all evidence lifecycle events.
- Audit trails for all access (`EvidenceAccessLog`).
- (Mock) Digital signatures for compliance logging.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
uvicorn src.main:app --reload --port 4002
```
