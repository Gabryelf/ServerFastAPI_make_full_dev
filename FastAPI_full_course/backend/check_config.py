import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.config import settings

    print("✅ Config module imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def check_config():
    print("=== Checking Configuration ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f".env file exists: {os.path.exists('.env')}")

    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            print(".env content:")
            print(f.read())

    print(f"DATABASE_TYPE from settings: {settings.DATABASE_TYPE}")
    print(f"Database URL: {settings.database_url}")
    print("==============================")


if __name__ == "__main__":
    check_config()