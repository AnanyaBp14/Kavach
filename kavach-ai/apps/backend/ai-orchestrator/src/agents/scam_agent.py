from src.agents.base import BaseAgent
from src.schemas.ai import ScamDetectionOutput
import json

class ScamDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScamDetectionAgent")
        
    async def analyze(self, complaint_text: str, metadata: dict) -> ScamDetectionOutput:
        prompt_template = self.load_prompt("scam_detection.md")
        
        context = {
            "text": complaint_text,
            "metadata": metadata
        }
        prompt_text = prompt_template.replace("{context}", json.dumps(context, indent=2))
        
        return await self.execute_with_retry(prompt_text, ScamDetectionOutput)

scam_agent = ScamDetectionAgent()
