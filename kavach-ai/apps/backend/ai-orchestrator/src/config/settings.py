from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Orchestrator Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # LLM Config
    GROQ_API_KEY: str = "mock-groq-key-for-local-testing"
    REASONING_MODEL: str = "llama-3.3-70b-versatile"
    FALLBACK_MODEL: str = "llama-3.1-8b-instant"

    # Kafka
    KAFKA_BROKER: str = "localhost:9092"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Neo4j
    NEO4J_URI: str = "neo4j://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "kavachpass"
    
    # AI Confidence Weights
    WEIGHTS: Dict[str, float] = {
        "scam_detection": 0.35,
        "fraud_network": 0.25,
        "counterfeit_currency": 0.15,
        "geospatial": 0.15,
        "officer_rules": 0.10
    }
    
    # Versioning
    WORKFLOW_VERSION: str = "v1"
    PROMPT_VERSION: str = "v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
