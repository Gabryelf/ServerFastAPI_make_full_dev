import mysql.connector
from mysql.connector import Error
from typing import Any, Dict, List, Optional
import logging
from .base import DatabaseInterface

logger = logging.getLogger(__name__)


class MySQLAdapter(DatabaseInterface):

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    async def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            if self.connection.is_connected():
                logger.info(f"Connected to MySQL database: {self.database}")
                return True
        except Error as e:
            logger.error(f"MySQL connection error: {e}")
        return False

    async def disconnect(self) -> bool:
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
            return True
        return False

    async def execute_query(self, query: str, params: Dict = None) -> Any:
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or {})

            if query.strip().lower().startswith('select'):
                result = cursor.fetchall()
            else:
                result = cursor.rowcount

            cursor.close()
            return result
        except Error as e:
            logger.error(f"!!!MySQL query error: {e}")
            raise

    async def fetch_one(self, query: str, params: Dict = None) -> Optional[Dict]:
        result = await self.execute_query(query, params)
        return result[0] if result else None

    async def fetch_all(self, query: str, params: Dict = None) -> List[Dict]:
        return await self.execute_query(query, params)
