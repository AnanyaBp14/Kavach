import os
import structlog
import asyncio
from sqlalchemy import select
from sklearn.cluster import DBSCAN
import numpy as np
import uuid
import json
from datetime import datetime, timezone
from src.database.session import async_session_factory
from src.database.models import GeoIncident, Hotspot
from src.services.redis_client import redis_cache

logger = structlog.get_logger()

class SpatialAnalyticsEngine:
    
    async def recompute_district_hotspots(self, district: str):
        if os.environ.get("TESTING") == "1":
            return
            
        logger.info("Recomputing hotspots", district=district)
        
        async with async_session_factory() as session:
            # 1. Fetch incidents
            result = await session.execute(
                select(GeoIncident).where(GeoIncident.district == district)
            )
            incidents = result.scalars().all()
            
            if not incidents or len(incidents) < 3:
                logger.info("Not enough incidents for clustering", district=district)
                return
                
            # 2. Extract coordinates (lat, lon)
            coords = np.array([[i.lat, i.lon] for i in incidents if i.lat and i.lon])
            if len(coords) < 3:
                return
                
            # 3. DBSCAN Clustering
            # roughly ~1km radius depending on location, epsilon in radians
            # 1 km / 6371 km (Earth radius) approx = 0.000157
            kms_per_radian = 6371.0088
            epsilon = 1.0 / kms_per_radian 
            
            db = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine')
            db.fit(np.radians(coords))
            
            # 4. Group by cluster
            labels = db.labels_
            unique_labels = set(labels)
            
            # Clear old hotspots for this district in DB (simplified approach for hackathon)
            # In production we might update them to keep historical IDs
            await session.execute(Hotspot.__table__.delete().where(Hotspot.district == district))
            
            for k in unique_labels:
                if k == -1: # Noise
                    continue
                    
                class_member_mask = (labels == k)
                cluster_coords = coords[class_member_mask]
                cluster_incidents = [incidents[i] for i in range(len(incidents)) if class_member_mask[i]]
                
                # Center point
                center_lat = np.mean(cluster_coords[:, 0])
                center_lon = np.mean(cluster_coords[:, 1])
                
                # Threat
                avg_threat = np.mean([i.threat_score for i in cluster_incidents])
                
                # Bounding radius (max distance from center)
                # approximation for UI drawing (in meters)
                radius = 500.0 
                
                # Confidence based on density
                confidence = min(0.99, len(cluster_coords) * 0.05 + 0.5)
                
                # Explanation
                reasons = [
                    f"High concentration of {len(cluster_coords)} incidents",
                    f"Average threat score is {avg_threat:.2f}"
                ]
                
                hotspot = Hotspot(
                    id=str(uuid.uuid4()),
                    lat=center_lat,
                    lon=center_lon,
                    location=f"POINT({center_lon} {center_lat})",
                    radius=radius,
                    incident_count=len(cluster_coords),
                    average_threat=avg_threat,
                    cluster_score=avg_threat * (len(cluster_coords)/10),
                    confidence=confidence,
                    trend="Increasing",
                    reasons=json.dumps(reasons),
                    district=district
                )
                
                session.add(hotspot)
                
            await session.commit()
            
            # Invalidate cache
            await redis_cache.delete_by_prefix(f"geo:hotspots:{district}")
            await redis_cache.delete_by_prefix("geo:hotspots:all")

spatial_engine = SpatialAnalyticsEngine()
