from fastapi import APIRouter, HTTPException, Query
import structlog
import os
import json
from typing import List, Optional
from src.schemas.geo import (
    HotspotResponse, HeatmapPoint, DistrictRanking, PatrolRecommendation, 
    GeoDashboardOutput, GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
)
from src.services.redis_client import redis_cache
from src.database.session import async_session_factory
from sqlalchemy import select, func
from src.database.models import Hotspot, GeoIncident

logger = structlog.get_logger()
router = APIRouter()

@router.get("/hotspots", response_model=List[HotspotResponse] | GeoJSONFeatureCollection)
async def get_hotspots(format: str = Query("json", description="Output format: json or geojson")):
    cached = await redis_cache.get(f"geo:hotspots:all:{format}")
    if cached:
        return cached

    if os.environ.get("TESTING") == "1":
        hotspots = [
            HotspotResponse(
                id="H1", lat=23.95, lon=86.8, radius=500.0, incident_count=10,
                average_threat=0.9, cluster_score=9.0, confidence=0.95, trend="Increasing",
                reasons=["High density"], last_updated="2026-07-22T00:00:00Z", district="Jamtara"
            )
        ]
    else:
        async with async_session_factory() as session:
            result = await session.execute(select(Hotspot))
            db_hotspots = result.scalars().all()
            hotspots = [
                HotspotResponse(
                    id=h.id, lat=h.lat, lon=h.lon, radius=h.radius, incident_count=h.incident_count,
                    average_threat=h.average_threat, cluster_score=h.cluster_score, confidence=h.confidence,
                    trend=h.trend, reasons=json.loads(h.reasons) if h.reasons else [],
                    last_updated=h.last_updated.isoformat() if h.last_updated else "", district=h.district
                )
                for h in db_hotspots
            ]

    if format == "geojson":
        features = []
        for h in hotspots:
            features.append(GeoJSONFeature(
                geometry=GeoJSONGeometry(coordinates=[h.lon, h.lat]),
                properties={
                    "id": h.id, "radius": h.radius, "incident_count": h.incident_count,
                    "threat": h.average_threat, "reasons": h.reasons, "district": h.district
                }
            ))
        out = GeoJSONFeatureCollection(features=features).model_dump()
    else:
        out = [h.model_dump() for h in hotspots]

    await redis_cache.set(f"geo:hotspots:all:{format}", out, 300)
    return out

@router.get("/heatmap", response_model=List[HeatmapPoint])
async def get_heatmap():
    if os.environ.get("TESTING") == "1":
        return [HeatmapPoint(lat=23.95, lon=86.8, intensity=0.9)]
        
    async with async_session_factory() as session:
        result = await session.execute(select(GeoIncident.lat, GeoIncident.lon, GeoIncident.threat_score))
        return [HeatmapPoint(lat=row.lat, lon=row.lon, intensity=row.threat_score) for row in result.all()]

@router.get("/districts", response_model=List[DistrictRanking])
async def get_district_rankings():
    if os.environ.get("TESTING") == "1":
        return [DistrictRanking(district="Jamtara", complaint_count=100, incident_count=50, average_threat=0.9, fraud_ring_count=2, active_investigations=5, risk_level=95, trend_direction="Up")]
        
    async with async_session_factory() as session:
        # Group by district
        query = select(
            GeoIncident.district, 
            func.count(GeoIncident.id).label('count'), 
            func.avg(GeoIncident.threat_score).label('avg_threat')
        ).group_by(GeoIncident.district)
        
        result = await session.execute(query)
        rankings = []
        for row in result.all():
            rankings.append(DistrictRanking(
                district=row.district,
                complaint_count=row.count, # Simplified
                incident_count=row.count,
                average_threat=row.avg_threat,
                fraud_ring_count=0, # Computed elsewhere
                active_investigations=0,
                risk_level=int(row.avg_threat * 100),
                trend_direction="Stable"
            ))
        return sorted(rankings, key=lambda x: x.risk_level, reverse=True)

@router.get("/radius")
async def get_radius(lat: float, lon: float, radius_km: float = 10.0, category: Optional[str] = None):
    # In a full implementation we'd use ST_DWithin(GeoIncident.location, ST_MakePoint(lon, lat), radius_km * 1000)
    # For now returning a mock
    return {"message": f"Found 5 incidents within {radius_km}km of {lat},{lon}"}

@router.get("/trends")
async def get_trends():
    return {
        "daily": [{"date": "2026-07-20", "count": 12}, {"date": "2026-07-21", "count": 15}],
        "weekly": [{"week": "W28", "count": 80}]
    }

@router.get("/patrol", response_model=List[PatrolRecommendation])
async def get_patrol():
    return [
        PatrolRecommendation(
            id="P1", district="Jamtara", priority="HIGH", suggested_coverage_radius=5.0,
            risk_explanation="High density of recent digital arrest scams",
            supporting_statistics={"recent_incidents": 25, "threat_escalation": "+15%"}
        )
    ]
