from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone

# Base Agent Response
class AgentResponse(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    limitations: List[str] = Field(default_factory=list)
    reasoning: str
    recommendation: str

# Specific Agent Outputs extending Base
class ScamDetectionOutput(AgentResponse):
    category: str
    matched_patterns: List[str] = Field(default_factory=list)

class CurrencyAnalysisOutput(AgentResponse):
    extracted_serial_number: Optional[str] = None
    missing_security_features: List[str] = Field(default_factory=list)

class ThreatFusionOutput(AgentResponse):
    overall_threat: str
    top_factors: List[str] = Field(default_factory=list)

class CopilotOutput(AgentResponse):
    investigation_summary: str
    legal_notes: str
    checklist: List[str] = Field(default_factory=list)

# Timeline Event
class TimelineEvent(BaseModel):
    step: str
    agent: str
    status: str
    confidence: Optional[float] = None
    duration_ms: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Request Schemas
class AIAnalysisRequest(BaseModel):
    complaint_id: str
    text_content: Optional[str] = None
    evidence_urls: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Final Response Schema
class AIAnalysisResponse(BaseModel):
    session_id: str
    overall_threat: Optional[str] = None
    unified_score: Optional[float] = None
    investigation_summary: Optional[str] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    model_version: str
    workflow_version: str
    prompt_version: str
