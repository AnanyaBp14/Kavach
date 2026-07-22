from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Geospatial Intelligence Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Connections
    KAFKA_BROKER: str = "localhost:9092"
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:kavachpass@localhost:5434/geo_db"
    REDIS_URL: str = "redis://localhost:6381/1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
