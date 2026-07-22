from fastapi import APIRouter, Depends
from src.database.session import get_redis
import redis.asyncio as aioredis
from typing import Dict, Any

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    redis: aioredis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    # Mocking redis data for now; in a real app, kafka consumers or cron jobs update these.
    total_complaints = await redis.get("dashboard:total_complaints") or 0
    open_cases = await redis.get("dashboard:open_cases") or 0
    active_officers = await redis.get("dashboard:active_officers") or 0
    
    return {
        "total_complaints": int(total_complaints),
        "open_cases": int(open_cases),
        "active_officers": int(active_officers),
    }

@router.get("/threats")
async def get_threat_distribution(
    redis: aioredis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    threats = await redis.hgetall("dashboard:threats")
    return threats if threats else {"Red": 0, "Orange": 0, "Yellow": 0}

@router.get("/districts")
async def get_district_stats(
    redis: aioredis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    districts = await redis.hgetall("dashboard:districts")
    return districts if districts else {"Delhi": 0, "Mumbai": 0}

@router.get("/trends")
async def get_trends(
    redis: aioredis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    trends = await redis.hgetall("dashboard:daily_trends")
    return trends if trends else {}
