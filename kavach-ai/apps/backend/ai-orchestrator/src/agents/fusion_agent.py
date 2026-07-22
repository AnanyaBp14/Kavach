from src.agents.base import BaseAgent
from src.schemas.ai import ThreatFusionOutput
from src.config.settings import settings
import json

class ThreatFusionAgent(BaseAgent):
    def __init__(self):
        super().__init__("ThreatFusionAgent")
        
    async def analyze(self, agent_outputs: dict) -> ThreatFusionOutput:
        prompt_template = self.load_prompt("threat_fusion.md")
        
        # Serialize the outputs for the prompt
        context = {k: v.model_dump() for k, v in agent_outputs.items() if v is not None}
        
        prompt_text = prompt_template.replace("{context}", json.dumps(context, indent=2))
        prompt_text = prompt_text.replace("{weights}", json.dumps(settings.WEIGHTS, indent=2))
        
        return await self.execute_with_retry(prompt_text, ThreatFusionOutput)

fusion_agent = ThreatFusionAgent()
