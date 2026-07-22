# KAVACH AI - AI Orchestrator

The AI Orchestrator is the central brain of KAVACH AI. It executes a LangGraph workflow that coordinates multiple parallel AI agents and fuses their outputs to generate a unified Threat Assessment and Officer Copilot recommendation.

## Agents Implemented
1. **Scam Detection Agent**: Analyzes text for Digital Arrest / Phishing patterns using LLaMA.
2. **Counterfeit Currency Agent**: Analyzes images for fake currency using EasyOCR, OpenCV, and LLaMA.
3. **Fraud Network Agent**: Extracts entities (Phone, UPI, Account) and writes them to Neo4j.
4. **Geospatial Intelligence Agent**: Looks up coordinates against known cybercrime hotspots.
5. **Threat Fusion Agent**: Fuses parallel agent outputs using weighted scores.
6. **Officer Copilot Agent**: Translates the unified threat into an actionable summary and checklist.

## Architecture
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Workflow Engine**: LangGraph & LangChain
- **AI Models**: Groq (LLaMA 3.3 70B & 3.1 8B), Sentence Transformers, EasyOCR
- **Graph Database**: Neo4j
- **Eventing**: Kafka (aiokafka)
- **Memory Layer**: Redis

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
uvicorn src.main:app --reload --port 4003
```
