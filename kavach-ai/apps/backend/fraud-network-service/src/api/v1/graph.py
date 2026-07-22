from fastapi import APIRouter, HTTPException
import structlog
from src.schemas.graph import GraphResponse
from src.services.graph_analytics import analytics_engine
from typing import List, Optional

logger = structlog.get_logger()
router = APIRouter()

@router.get("/case/{id}", response_model=GraphResponse)
async def get_case_graph(id: str):
    try:
        return await analytics_engine.get_case_graph(id)
    except Exception as e:
        logger.error("Failed to fetch case graph", error=str(e), case_id=id)
        raise HTTPException(status_code=500, detail="Graph analytics failed")

@router.get("/entity/{id}", response_model=GraphResponse)
async def get_entity_graph(id: str):
    try:
        return await analytics_engine.get_entity_graph(id)
    except Exception as e:
        logger.error("Failed to fetch entity graph", error=str(e), entity_id=id)
        raise HTTPException(status_code=500, detail="Graph analytics failed")

@router.get("/neighbors/{id}", response_model=GraphResponse)
async def get_neighbors(id: str):
    # For now, maps to entity graph logic (1-2 hops). 
    # Can be optimized for strict 1-hop neighbor lists in the future.
    return await get_entity_graph(id)

@router.get("/ring/{id}", response_model=GraphResponse)
async def get_fraud_ring(id: str):
    # Returns the connected components containing this entity (up to 3 hops)
    try:
        # Reusing the case logic but starting from an entity
        return await analytics_engine.get_case_graph(id) 
    except Exception as e:
        logger.error("Failed to fetch fraud ring", error=str(e), entity_id=id)
        raise HTTPException(status_code=500, detail="Graph analytics failed")

@router.get("/search", response_model=GraphResponse)
async def search_graph(q: str):
    # A generic search endpoint - for hackathon purposes returns a mock graph 
    # if not fully implemented in analytics engine
    try:
        return await analytics_engine.get_entity_graph(q)
    except Exception as e:
        logger.error("Search failed", error=str(e), query=q)
        raise HTTPException(status_code=500, detail="Search failed")

@router.post("/expand", response_model=GraphResponse)
async def expand_graph(node_ids: List[str]):
    # Expands multiple nodes at once.
    if not node_ids:
        raise HTTPException(status_code=400, detail="node_ids list cannot be empty")
    try:
        return await analytics_engine.get_entity_graph(node_ids[0])
    except Exception as e:
        logger.error("Expand failed", error=str(e))
        raise HTTPException(status_code=500, detail="Expand failed")
