from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from models import User, UserCreate
from auth import auth_service
from products import product_service
from orders import order_service
from pathlib import Path

BACKEND_DIR = Path(__file__).parent
STATIC_DIR = BACKEND_DIR / "static"

app = FastAPI(title="Marketplace")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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


@app.get("/")
def read_root():
    index_path = STATIC_DIR / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
