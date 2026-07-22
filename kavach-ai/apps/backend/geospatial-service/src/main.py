from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog
from contextlib import asynccontextmanager

from src.config.settings import settings
from src.database.session import init_db
from src.services.redis_client import redis_cache
from src.consumers.kafka_consumer import kafka_consumer
from src.middleware.structlog_middleware import StructlogMiddleware
from src.api.v1.geo import router as geo_router

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await redis_cache.connect()
    await kafka_consumer.start()
    logger.info("Application startup complete")
    yield
    # Shutdown
    await kafka_consumer.stop()
    await redis_cache.close()
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
    return {"status": "READY"}

app.include_router(geo_router, prefix=f"{settings.API_V1_STR}/geo", tags=["Geospatial Intelligence"])
