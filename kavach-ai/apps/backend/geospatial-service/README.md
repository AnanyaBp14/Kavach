# KAVACH AI - Geospatial Intelligence Service

The Geospatial Intelligence Service provides spatial analytics, hotspot detection, incident clustering, and jurisdiction intelligence.

It relies on a PostGIS database and uses `scikit-learn` DBSCAN clustering to identify geographic fraud hotspots.

## Architecture
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL with PostGIS extension (GeoAlchemy2)
- **Caching**: Redis
- **Eventing**: Kafka (aiokafka)

## Key Features
- **Spatial Clustering**: Background tasks recompute DBSCAN clusters per district upon new incident arrival.
- **GeoJSON Output**: All map endpoints (`/hotspots`, etc.) support `?format=geojson` natively for direct ingestion by Leaflet/Mapbox on the frontend.
- **Detailed Explainability**: Hotspots return confidence scores, incident density metrics, and dynamic `reasons`.
- **Temporal Trends & Heatmaps**: Provides aggregated threat densities and time-series data for dashboard visualizations.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
uvicorn src.main:app --reload --port 4005
```
