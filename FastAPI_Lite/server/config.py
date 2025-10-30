import os


class Settings:
    APP_NAME: str = "Marketplace API"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8001))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    STATIC_DIR: str = "D:/ServerFastAPI/FastAPI_Lite/server"
    TEMPLATES_DIR: str = "D:/ServerFastAPI/FastAPI_Lite/server/templates"


settings = Settings()
