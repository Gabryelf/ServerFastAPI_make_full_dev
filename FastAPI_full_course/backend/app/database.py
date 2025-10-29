from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    if settings.DATABASE_TYPE == 'mysql':
        # Подключаемся без указания базы данных
        temp_url = f"mysql+mysqlconnector://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/"
        temp_engine = create_engine(temp_url)

        try:
            with temp_engine.connect() as conn:
                # Проверяем существует ли база данных
                result = conn.execute(text(f"SHOW DATABASES LIKE '{settings.MYSQL_DB}'"))
                database_exists = result.fetchone() is not None

                if not database_exists:
                    logger.info(f"Creating database {settings.MYSQL_DB}...")
                    conn.execute(text(f"CREATE DATABASE {settings.MYSQL_DB}"))
                    conn.commit()
                    logger.info(f"Database {settings.MYSQL_DB} created successfully")
                else:
                    logger.info(f"Database {settings.MYSQL_DB} already exists")

        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise
        finally:
            temp_engine.dispose()


# Choose database based on configuration
if settings.DATABASE_TYPE == 'mysql':
    # Сначала создаем базу если нужно
    create_database_if_not_exists()

    # Затем подключаемся к конкретной базе
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=True  # Включим echo для отладки
    )
else:
    # PostgreSQL
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=True  # Включим echo для отладки
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database"""
    from . import models
    try:
        logger.info(f"Creating tables for {settings.DATABASE_TYPE} database...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def create_admin_user(db):
    """Create admin user if not exists"""
    from .crud import create_user
    from .schemas import UserCreate
    from .models import User

    try:
        admin_user = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin_user:
            user_data = UserCreate(
                email="admin@admin.com",
                password="admin123",
                full_name="Admin User"
            )
            create_user(db, user_data, is_admin=True)
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise


def init_db():
    """Initialize database with tables and admin user"""
    create_tables()
    db = SessionLocal()
    try:
        create_admin_user(db)
    finally:
        db.close()