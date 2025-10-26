from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """Настройка CORS для frontend на порту 4000"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4000",
            "http://127.0.0.1:4000"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )