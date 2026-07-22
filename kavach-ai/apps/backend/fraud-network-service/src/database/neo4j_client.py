import os
from neo4j import AsyncGraphDatabase
import structlog
from src.config.settings import settings

logger = structlog.get_logger()

class Neo4jClient:
    def __init__(self):
        self.driver = None

    async def connect(self):
        if os.environ.get("TESTING") == "1":
            return
            
        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            await self.verify_connectivity()
            await self._create_indexes()
            logger.info("Connected to Neo4j successfully")
        except Exception as e:
            logger.error("Failed to connect to Neo4j", error=str(e))

    async def verify_connectivity(self):
        async with self.driver.session() as session:
            await session.run("RETURN 1")
            
    async def _create_indexes(self):
        # Create indexes on frequently queried properties as recommended
        indexes = [
            "CREATE INDEX phone_idx IF NOT EXISTS FOR (p:Phone) ON (p.id)",
            "CREATE INDEX upi_idx IF NOT EXISTS FOR (u:UPI) ON (u.id)",
            "CREATE INDEX account_idx IF NOT EXISTS FOR (a:BankAccount) ON (a.id)",
            "CREATE INDEX complaint_idx IF NOT EXISTS FOR (c:Complaint) ON (c.id)",
            "CREATE INDEX citizen_idx IF NOT EXISTS FOR (c:Citizen) ON (c.id)",
        ]
        async with self.driver.session() as session:
            for idx in indexes:
                await session.run(idx)

    async def close(self):
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
            
    async def execute_query(self, query: str, parameters: dict = None):
        if os.environ.get("TESTING") == "1":
            logger.info("TESTING MODE: Query skipped", query=query)
            return []
            
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()

neo4j_client = Neo4jClient()
