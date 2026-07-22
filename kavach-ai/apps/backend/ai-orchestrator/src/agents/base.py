import os
import json
from langchain_groq import ChatGroq
from src.config.settings import settings
import structlog
from pydantic import BaseModel
import time

logger = structlog.get_logger()

class BaseAgent:
    def __init__(self, name: str, fallback: bool = False):
        self.name = name
        model_name = settings.FALLBACK_MODEL if fallback else settings.REASONING_MODEL
        self.llm = ChatGroq(
            temperature=0.0,
            groq_api_key=settings.GROQ_API_KEY,
            model_name=model_name
        )
        
    def load_prompt(self, filename: str) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", filename)
        with open(prompt_path, "r") as f:
            return f.read()

    async def execute_with_retry(self, prompt_text: str, schema_cls: type[BaseModel], max_retries: int = 2):
        for attempt in range(max_retries):
            try:
                if os.environ.get("TESTING") == "1":
                    # Mock response during testing
                    return self._mock_response(schema_cls)
                    
                messages = [("system", prompt_text)]
                
                # Using with_structured_output for guaranteed JSON schema
                structured_llm = self.llm.with_structured_output(schema_cls)
                response = await structured_llm.ainvoke(messages)
                return response
                
            except Exception as e:
                logger.error("Agent execution failed", agent=self.name, attempt=attempt, error=str(e))
                if attempt == max_retries - 1:
                    # Switch to fallback model or raise
                    logger.warning("Max retries reached. Failing gracefully.", agent=self.name)
                    raise
                time.sleep(1)
                
    def _mock_response(self, schema_cls: type[BaseModel]):
        # Very basic mocking based on schema fields
        mock_data = {
            "score": 0.8,
            "confidence": 0.9,
            "limitations": ["Mock limitation"],
            "reasoning": "Mock reasoning",
            "recommendation": "Mock recommendation",
            "category": "DIGITAL_ARREST",
            "overall_threat": "HIGH",
            "investigation_summary": "Mock summary",
            "legal_notes": "Mock notes"
        }
        # Filter mock_data to only include keys present in the schema
        filtered_data = {k: v for k, v in mock_data.items() if k in schema_cls.model_fields}
        return schema_cls(**filtered_data)
