from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog
import uuid

from src.config.settings import settings
from src.producers.kafka_producer import kafka_producer
from src.database.session import engine

from src.api.v1.complaints import router as complaints_router
from src.api.v1.incidents import router as incidents_router
from src.api.v1.cases import router as cases_router
from src.api.v1.officers import router as officers_router
from src.api.v1.dashboard import router as dashboard_router
from src.middleware.structlog_middleware import StructlogMiddleware

logger = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc"
)

app.add_middleware(StructlogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    await kafka_producer.start()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.stop()
    await engine.dispose()
    logger.info("Application shutdown complete")

# Health endpoints
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

# API Routes
app.include_router(complaints_router, prefix=f"{settings.API_V1_STR}/complaints", tags=["Complaints"])
app.include_router(incidents_router, prefix=f"{settings.API_V1_STR}/incidents", tags=["Incidents"])
app.include_router(cases_router, prefix=f"{settings.API_V1_STR}/cases", tags=["Cases"])
app.include_router(officers_router, prefix=f"{settings.API_V1_STR}/officers", tags=["Officers"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
