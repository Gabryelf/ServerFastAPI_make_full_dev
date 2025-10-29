import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.database import SessionLocal, init_db
    from app.config import settings
    from sqlalchemy import text  # Добавляем импорт text

    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Current directory:", os.getcwd())
    print("Python path:", sys.path)
    sys.exit(1)


def test_database():
    try:
        print("=== Testing MySQL Database Connection ===")
        print(f"Database Type: {settings.DATABASE_TYPE}")
        print(f"Database URL: {settings.database_url}")

        # Инициализируем базу
        print("Initializing database...")
        init_db()
        print("✅ Database initialization successful")

        # Тестируем подключение с правильным SQL выражением
        print("Testing database connection...")
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))  # Используем text()
        print(f"✅ Database connection successful - Result: {result.scalar()}")
        db.close()

        # Проверяем таблицы
        print("Checking tables...")
        db = SessionLocal()
        result = db.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        print(f"✅ Tables in database: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        db.close()

        print("=== MySQL Database Test Completed Successfully ===")

    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_database()