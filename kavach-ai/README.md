# KAVACH AI: National Intelligence Platform

KAVACH AI is an event-driven, microservices-based intelligence platform designed to ingest citizen complaints, orchestrate AI analysis, compute geospatial hotspots, and link fraud networks in near real-time.

## Features
- **Event-Driven Architecture**: Powered by Kafka, enabling asynchronous, non-blocking intelligence generation.
- **Explainable AI**: LangGraph and Llama-3 orchestrate targeted agents (Scam Detection, Threat Fusion) to provide transparent reasoning.
- **Geospatial Intelligence**: PostGIS-powered DBSCAN clustering detects threat hotspots on the fly.
- **Graph Analytics**: Neo4j maps multi-hop fraud rings connecting isolated complaints across jurisdictions.
- **Resilient Visualization**: A Next.js Command Center that degrades gracefully if individual microservices fail.

## Quick Start
To run the full stack locally for demonstration:

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
2. Start the infrastructure (13 containers):
   ```bash
   docker compose up -d
   ```
3. Run the smoke tests:
   ```bash
   python scripts/smoke_test.py
   ```
4. Seed the demo data:
   ```bash
   python scripts/seed_demo_data.py
   ```
5. Open the Command Center at [http://localhost:3000](http://localhost:3000)

## Documentation
- [Architecture Details](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

## Tech Stack
- **Backend**: FastAPI, Python 3.12, SQLAlchemy, Structlog
- **Frontend**: Next.js 15, Tailwind CSS, React Query, Zustand
- **AI**: LangGraph, Groq Llama 3.3
- **Data**: PostgreSQL, PostGIS, Neo4j, Redis, MinIO, Kafka
