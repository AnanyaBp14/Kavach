import json
import redis.asyncio as aioredis
from src.config.settings import settings
from typing import Dict, Any, Optional

class AIMemoryLayer:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = 86400  # 24 hours

    def _key(self, session_id: str) -> str:
        return f"ai_session:{session_id}"

    async def get_context(self, session_id: str) -> Dict[str, Any]:
        data = await self.redis.get(self._key(session_id))
        if data:
            return json.loads(data)
        return {
            "complaint_context": None,
            "evidence_context": [],
            "threat_context": None,
            "officer_context": None,
            "timeline": []
        }

    async def update_context(self, session_id: str, updates: Dict[str, Any]) -> None:
        context = await self.get_context(session_id)
        
        # Merge dicts/lists smartly
        for key, value in updates.items():
            if isinstance(value, list) and isinstance(context.get(key), list):
                context[key].extend(value)
            elif isinstance(value, dict) and isinstance(context.get(key), dict):
                context[key].update(value)
            else:
                context[key] = value

        await self.redis.set(self._key(session_id), json.dumps(context), ex=self.ttl)

    async def add_timeline_event(self, session_id: str, event: Dict[str, Any]) -> None:
        context = await self.get_context(session_id)
        context["timeline"].append(event)
        await self.redis.set(self._key(session_id), json.dumps(context), ex=self.ttl)
        
    async def clear_context(self, session_id: str) -> None:
        await self.redis.delete(self._key(session_id))

memory_layer = AIMemoryLayer()
