from sqlalchemy.ext.asyncio import AsyncSession
from src.models.core import ThreatAssessment
from src.repositories.base import CRUDBase

class CRUDThreat(CRUDBase[ThreatAssessment]):
    pass

threat_repo = CRUDThreat(ThreatAssessment)
