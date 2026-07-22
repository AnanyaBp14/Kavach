# KAVACH AI - Fraud Network Intelligence Service

The Fraud Network Intelligence Service continuously builds and analyzes the Neo4j knowledge graph of cybercrime entities (Citizens, Phones, Bank Accounts, UPI IDs, Complaints, etc.).

It consumes fat Kafka events to perform idempotent graph updates (`MERGE` queries) without relying on synchronous API calls to other services.

## Architecture
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: Neo4j (Graph Database)
- **Eventing**: Kafka (aiokafka)

## Key Features
- **Fat Events**: Consumes rich events like `complaint.created` and builds graph topology (nodes + edges).
- **Pure Cypher Analytics**: Calculates connected components, risk scores, and fraud rings using raw Cypher queries, with support for Neo4j GDS fallback.
- **REST Investigation APIs**: Exposes `/neighbors`, `/ring`, `/search`, and `/expand` endpoints optimized for visualization in the National Cyber Command Center.
- **Explainability**: Computes an `overall_risk` score and returns specific graph-based reasons.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
uvicorn src.main:app --reload --port 4004
```
