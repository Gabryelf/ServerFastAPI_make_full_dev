import asyncio
import sys
import os
import aiohttp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_user_registration():
    base_url = "http://localhost:8001"

    async with aiohttp.ClientSession() as session:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpass123"
        }

        print("🧪 Testing user registration...")
        async with session.post(f"{base_url}/api/register", json=user_data) as response:
            result = await response.json()
            if response.status == 200:
                print("User registration successful:", result)
            else:
                print("User registration failed:", result)

        # Тестируем вход
        print("\nTesting user login...")
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }

        async with session.post(f"{base_url}/api/login", json=login_data) as response:
            result = await response.json()
            if response.status == 200:
                print("User login successful:", result)
            else:
                print("User login failed:", result)

        print("\n Testing users list...")
        async with session.get(f"{base_url}/api/users") as response:
            result = await response.json()
            print("Users list:", result)


if __name__ == "__main__":
    print("Running user system tests...")
    asyncio.run(test_user_registration())