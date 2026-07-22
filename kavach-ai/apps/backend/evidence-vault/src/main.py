from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog
from contextlib import asynccontextmanager

from src.config.settings import settings
from src.producers.kafka_producer import kafka_producer
from src.database.session import engine
from src.middleware.structlog_middleware import StructlogMiddleware
from src.api.v1.evidence import router as evidence_router

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await kafka_producer.start()
    logger.info("Application startup complete")
    yield
    await kafka_producer.stop()
    await engine.dispose()
    logger.info("Application shutdown complete")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(StructlogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
async def health_check():
    return {"status": "UP"}

@app.get("/live")
async def liveness_check():
    return {"status": "LIVE"}

@app.get("/ready")
async def readiness_check():
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "READY"}
    except Exception as e:
        return {"status": "NOT_READY", "error": str(e)}

app.include_router(evidence_router, prefix=f"{settings.API_V1_STR}/evidence", tags=["Evidence"])
