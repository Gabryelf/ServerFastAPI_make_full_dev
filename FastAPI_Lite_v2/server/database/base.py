from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseInterface(ABC):

    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        pass

    @abstractmethod
    async def execute_query(self, query: str, params: Dict = None) -> Any:
        pass

    @abstractmethod
    async def fetch_one(self, query: str, params: Dict = None) -> Optional[Dict]:
        pass

    @abstractmethod
    async def fetch_all(self, query: str, params: Dict = None) -> List[Dict]:
        pass


class DatabaseManager:

    def __init__(self):
        self.db: Optional[DatabaseInterface] = None
        self.connected = False

    async def initialize(self, db_interface: DatabaseInterface):
        self.db = db_interface
        self.connected = await self.db.connect()
        if self.connected:
            logger.info("✅ Database manager initialized successfully")
        else:
            logger.error("❌ Failed to initialize database manager")
        return self.connected

    async def close(self):
        if self.db and self.connected:
            await self.db.disconnect()
            self.connected = False
            logger.info("✅ Database connection closed")

    async def execute(self, query: str, params: Dict = None) -> Any:
        if not self.connected or not self.db:
            raise ConnectionError("Database not connected")
        return await self.db.execute_query(query, params)

    async def fetch_one(self, query: str, params: Dict = None) -> Optional[Dict]:
        if not self.connected or not self.db:
            raise ConnectionError("Database not connected")
        return await self.db.fetch_one(query, params)

    async def fetch_all(self, query: str, params: Dict = None) -> List[Dict]:
        if not self.connected or not self.db:
            raise ConnectionError("Database not connected")
        return await self.db.fetch_all(query, params)
    