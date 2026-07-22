from src.agents.base import BaseAgent
from src.schemas.ai import AgentResponse
from pydantic import Field
import os

class GeospatialOutput(AgentResponse):
    hotspot_score: float = Field(default=0.0)
    nearby_incidents: int = Field(default=0)

class GeospatialIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("GeospatialIntelligenceAgent")
        
    async def analyze(self, lat: float, lon: float, district: str) -> GeospatialOutput:
        if os.environ.get("TESTING") == "1":
            return GeospatialOutput(
                score=0.6,
                confidence=0.8,
                limitations=["Mocked geo lookup"],
                reasoning="Location is in a known medium-risk district",
                recommendation="Normal vigilance",
                hotspot_score=0.6,
                nearby_incidents=12
            )
            
        # Simulated geospatial risk based on district lookup
        high_risk_districts = ["Jamtara", "Mewat", "Bharatpur", "Mathura"]
        
        is_high_risk = district in high_risk_districts
        
        score = 0.9 if is_high_risk else 0.2
        reasoning = f"Originates from {district}, which is a {'known high-risk cybercrime hotspot' if is_high_risk else 'standard risk area'}."
        
        return GeospatialOutput(
            score=score,
            confidence=0.9,
            limitations=["Uses static district lists instead of dynamic density algorithms"],
            reasoning=reasoning,
            recommendation="Escalate if from known hotspot",
            hotspot_score=score,
            nearby_incidents=50 if is_high_risk else 2
        )

geo_agent = GeospatialIntelligenceAgent()
