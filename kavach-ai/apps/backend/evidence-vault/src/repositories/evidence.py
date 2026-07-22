from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.evidence import Evidence, ChainOfCustody, EvidenceAccessLog, DigitalSignature
from src.repositories.base import CRUDBase
from typing import List

class CRUDEvidence(CRUDBase[Evidence]):
    async def get_by_hash(self, db: AsyncSession, sha256_hash: str) -> Evidence | None:
        result = await db.execute(select(Evidence).filter(Evidence.sha256_hash == sha256_hash))
        return result.scalars().first()

class CRUDChainOfCustody(CRUDBase[ChainOfCustody]):
    async def get_timeline(self, db: AsyncSession, evidence_id: str) -> List[ChainOfCustody]:
        result = await db.execute(
            select(ChainOfCustody)
            .filter(ChainOfCustody.evidence_id == evidence_id)
            .order_by(ChainOfCustody.created_at.asc())
        )
        return list(result.scalars().all())

class CRUDEvidenceAccessLog(CRUDBase[EvidenceAccessLog]):
    async def get_logs(self, db: AsyncSession, evidence_id: str) -> List[EvidenceAccessLog]:
        result = await db.execute(
            select(EvidenceAccessLog)
            .filter(EvidenceAccessLog.evidence_id == evidence_id)
            .order_by(EvidenceAccessLog.created_at.desc())
        )
        return list(result.scalars().all())

class CRUDDigitalSignature(CRUDBase[DigitalSignature]):
    async def get_by_evidence(self, db: AsyncSession, evidence_id: str) -> DigitalSignature | None:
        result = await db.execute(select(DigitalSignature).filter(DigitalSignature.evidence_id == evidence_id))
        return result.scalars().first()

evidence_repo = CRUDEvidence(Evidence)
chain_repo = CRUDChainOfCustody(ChainOfCustody)
access_log_repo = CRUDEvidenceAccessLog(EvidenceAccessLog)
signature_repo = CRUDDigitalSignature(DigitalSignature)
