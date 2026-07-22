from src.agents.base import BaseAgent
from src.schemas.ai import CopilotOutput
import json

class OfficerCopilotAgent(BaseAgent):
    def __init__(self):
        super().__init__("OfficerCopilotAgent")
        
    async def analyze(self, threat_fusion: dict, complaint_context: dict) -> CopilotOutput:
        prompt_template = self.load_prompt("officer_copilot.md")
        
        context = {
            "threat_assessment": threat_fusion,
            "complaint_details": complaint_context
        }
        prompt_text = prompt_template.replace("{context}", json.dumps(context, indent=2))
        
        return await self.execute_with_retry(prompt_text, CopilotOutput)

copilot_agent = OfficerCopilotAgent()
