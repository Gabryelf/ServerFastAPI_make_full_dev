import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class Settings:

    APP_NAME: str = "Marketplace API"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8001))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    STATIC_DIR: str = str(BASE_DIR / "server" / "static")
    TEMPLATES_DIR: str = str(BASE_DIR / "server" / "templates")

    DB_TYPE: str = os.getenv("DB_TYPE", "mysql")  # mysql, postgres, mongodb
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "sksmel544332")
    DB_NAME: str = os.getenv("DB_NAME", "marketplace_db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    def get_db_url(self) -> str:
        if self.DB_TYPE == "mysql":
            return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_TYPE == "postgres":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"{self.DB_TYPE}://{self.DB_HOST}:{self.DB_PORT}"


settings = Settings()
