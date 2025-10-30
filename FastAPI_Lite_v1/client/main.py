import aiohttp
from typing import Dict, Any


class MarketplaceClient:
    """Базовый клиент для взаимодействия с сервером"""

    def __init__(self, base_url: str = "http://localhost:8001"):  # Обновляем порт
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def disconnect(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def health_check(self) -> Dict[str, Any]:
        await self.connect()
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return await response.json()
        except aiohttp.ClientError as e:
            return {"status": "error", "message": str(e)}

    async def get_lobby(self) -> str:
        await self.connect()
        try:
            async with self.session.get(self.base_url) as response:
                return await response.text()
        except aiohttp.ClientError as e:
            return f"Error: {str(e)}"
