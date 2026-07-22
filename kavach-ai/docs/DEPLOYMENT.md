# KAVACH AI: Deployment Guide

This guide explains how to spin up the entire KAVACH AI platform from scratch on a single machine for demonstration and development purposes.

## Prerequisites
- Docker Engine & Docker Compose (v2)
- Python 3.12 (for running seed scripts)
- Node.js 18+ (for local frontend dev, though the frontend is also containerized)

## Step 1: Environment Setup
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Ensure you add your `GROQ_API_KEY` to the `.env` file for the AI Orchestrator to function.

## Step 2: Spin Up Infrastructure
Start the entire stack using the master Docker Compose file:
```bash
docker compose up -d
```
This command will spin up 13 containers in the correct dependency order. Expect initial startup to take roughly 1-2 minutes as PostgreSQL, PostGIS, and Neo4j initialize.

## Step 3: Verify Health
Run the smoke test to ensure all services are healthy:
```bash
python scripts/smoke_test.py
```
You should see output indicating all 6 microservices are `UP`.

## Step 4: Seed Demo Data
To populate the databases with a rich historical dataset (Fraud rings, Geo-hotspots, Complaints):
```bash
pip install -r scripts/requirements.txt # (psycopg[binary], neo4j, kafka-python, minio)
python scripts/seed_demo_data.py
```

## Step 5: Access the Command Center
Open your browser and navigate to:
**http://localhost:3000**

You will see the National Cyber Command Center populated with the seeded data.

## Troubleshooting
- **Graph Not Updating**: Ensure Neo4j has sufficient RAM allocated in Docker desktop.
- **AI Processing Hanging**: Verify your `GROQ_API_KEY` is valid and hasn't hit rate limits.
- **Port Conflicts**: Ensure ports `4000-4005`, `3000`, `5432`, `5433`, `6379`, `9092`, `7474`, `7687`, and `9000` are free on your host machine.
