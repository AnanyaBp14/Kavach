from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GraphNode(BaseModel):
    id: str
    label: str
    properties: Dict[str, Any]
    # Dashboard hints
    group: str
    risk: int = 0
    size: int = 15

class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class RiskProfile(BaseModel):
    entity_risk: int
    community_risk: int
    path_risk: int
    overall_risk: int
    reasons: List[str]

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    risk_profile: RiskProfile
    ring_size: int = 0
    suspected_mastermind: Optional[str] = None
    money_mules: List[str] = Field(default_factory=list)
    recommended_entities: List[str] = Field(default_factory=list)
