from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime, timezone

Base = declarative_base()

class GeoIncident(Base):
    __tablename__ = "geo_incidents"
    
    id = Column(String, primary_key=True)
    complaint_id = Column(String, index=True)
    
    # Store both geometry and raw coordinates as requested
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    lat = Column(Float)
    lon = Column(Float)
    
    district = Column(String, index=True)
    state = Column(String)
    threat_score = Column(Float, default=0.0)
    category = Column(String)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Hotspot(Base):
    __tablename__ = "geo_hotspots"
    
    id = Column(String, primary_key=True)
    center = Column(Geometry(geometry_type='POINT', srid=4326))
    lat = Column(Float)
    lon = Column(Float)
    
    radius = Column(Float)  # in meters
    incident_count = Column(Integer)
    average_threat = Column(Float)
    cluster_score = Column(Float)
    confidence = Column(Float)
    trend = Column(String)
    
    # Reasons will be stored as JSON string or array in Postgres (using String for simplicity across DBs)
    reasons = Column(String)
    
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    district = Column(String, index=True)

class PatrolZone(Base):
    __tablename__ = "geo_patrol_zones"
    
    id = Column(String, primary_key=True)
    district = Column(String, index=True)
    priority = Column(String) # HIGH, MEDIUM, LOW
    recommendation = Column(String)
    risk_level = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
