from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_TYPE: Literal['postgresql', 'mysql'] = 'postgresql'

    # PostgreSQL
    POSTGRES_DB: str = "marketplace"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # MySQL
    MYSQL_DB: str = "marketplace"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "sksmel544332"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"

    # Application
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def database_url(self) -> str:
        if self.DATABASE_TYPE == 'postgresql':
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        env_file = ".env"


settings = Settings()