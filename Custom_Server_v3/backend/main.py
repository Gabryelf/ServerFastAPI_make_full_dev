from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from models import User, UserCreate
from auth import auth_service
from products import product_service
from orders import order_service
from pathlib import Path
import os

# Получаем настройки из переменных окружения
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Пути для Docker
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Simple Marketplace",
    description="Educational marketplace example",
    version="1.0.0"
)

# Монтируем статические файлы фронтенда
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
else:
    # Fallback для Docker
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# API endpoints
@app.post("/register")
def register(user_data: UserCreate):
    return auth_service.register_user(user_data)


@app.get("/products")
def get_products():
    return product_service.get_all_products()


@app.post("/products")
def create_product(name: str, price: float, description: str, user: User = Depends(auth_service.get_current_user)):
    if user.role not in ['seller', 'admin']:
        raise HTTPException(status_code=403, detail="Только продавцы могут добавлять товары")

    return product_service.create_product(name, price, description, user.id)


@app.post("/buy/{product_id}")
def buy_product(product_id: int, user: User = Depends(auth_service.get_current_user)):
    return order_service.create_order(user.id, product_id)


@app.get("/my-orders")
def get_my_orders(user: User = Depends(auth_service.get_current_user)):
    return order_service.get_user_orders(user.id)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "marketplace"}


@app.get("/")
def read_root():
    # Пытаемся найти index.html в разных местах
    possible_paths = [
        FRONTEND_DIR / "index.html",
        Path(__file__).parent / "static" / "index.html",
        Path("static/index.html"),
        Path("../frontend/index.html")
    ]

    for index_path in possible_paths:
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())

    return HTMLResponse(content="<h1>Marketplace Backend is Running</h1><p>Frontend files not found</p>")


if __name__ == "__main__":
    import uvicorn

    print(f"Starting server on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
