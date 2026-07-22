from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class HotspotResponse(BaseModel):
    id: str
    lat: float
    lon: float
    radius: float
    incident_count: int
    average_threat: float
    cluster_score: float
    confidence: float
    trend: str
    reasons: List[str]
    last_updated: str
    district: str

class HeatmapPoint(BaseModel):
    lat: float
    lon: float
    intensity: float

class DistrictRanking(BaseModel):
    district: str
    complaint_count: int
    incident_count: int
    average_threat: float
    fraud_ring_count: int
    active_investigations: int
    risk_level: int
    trend_direction: str

class PatrolRecommendation(BaseModel):
    id: str
    district: str
    priority: str
    suggested_coverage_radius: float
    risk_explanation: str
    supporting_statistics: Dict[str, Any]

class GeoDashboardOutput(BaseModel):
    hotspots: List[HotspotResponse]
    district_rankings: List[DistrictRanking]
    heatmap: List[HeatmapPoint]
    patrol_recommendations: List[PatrolRecommendation]
    summary: Dict[str, Any]

# GeoJSON Schemas
class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [lon, lat]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
