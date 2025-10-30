import asyncio
import sys
import os
from client.main import MarketplaceClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_basic_functionality():
    async with MarketplaceClient("http://localhost:8001") as client:
        # Тестируем health check
        health = await client.health_check()
        print("Health check:", health)

        # Тестируем получение лобби
        lobby = await client.get_lobby()
        print("Lobby page received:", len(lobby), "characters")

        # Проверяем клиентский health endpoint
        client_health = await client.session.get("http://localhost:8001/api/client/health")
        client_health_data = await client_health.json()
        print("Client health check:", client_health_data)


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
