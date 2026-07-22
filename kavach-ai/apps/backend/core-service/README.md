# KAVACH AI - Core Intelligence Service

The Core Intelligence Service is the central business domain of the KAVACH AI Public Safety Platform. It manages Complaints, Incidents, Cases, Threats, and Officer Assignments.

## Architecture
- **Language**: Python 3.12
- **Framework**: FastAPI (Uvicorn)
- **Database**: PostgreSQL (SQLAlchemy 2.0 Async, Alembic)
- **Validation**: Pydantic v2
- **Event Streaming**: Kafka (KRaft mode) via `aiokafka`
- **Caching**: Redis
- **Logging**: Structlog (JSON)
- **Observability**: Prometheus (`prometheus-client`)

## Features
- Full lifecycle management (Complaints -> Incidents -> Cases)
- Soft deletes & audit trails via TimelineEvents/StatusHistory
- Kafka KRaft integration for event publishing (`complaint.created`, `incident.updated`, etc.)
- Redis-backed Dashboard aggregation
- Clean Architecture (API -> Service -> Repository -> Models)

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
uvicorn src.main:app --reload --port 4001
```
