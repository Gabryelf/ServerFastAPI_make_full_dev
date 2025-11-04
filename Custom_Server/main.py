from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import hashlib
import os

app = FastAPI(title="Simple Marketplace")
app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()


# Модели данных
class User(BaseModel):
    id: int
    username: str
    role: str  # 'customer', 'seller', 'admin'


class Product(BaseModel):
    id: int
    name: str
    price: float
    seller_id: int
    description: str = ""


class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    status: str  # 'pending', 'paid', 'shipped'


# Инициализация БД
def init_db():
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            seller_id INTEGER,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            status TEXT
        )
    ''')

    # Добавляем тестовые данные
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("admin", hash_password("admin"), "admin"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("seller1", hash_password("123"), "seller"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("customer1", hash_password("123"), "customer"))

        cursor.execute("INSERT INTO products (name, price, seller_id, description) VALUES (?, ?, ?, ?)",
                       ("Ноутбук", 50000, 2, "Мощный игровой ноутбук"))
        cursor.execute("INSERT INTO products (name, price, seller_id, description) VALUES (?, ?, ?, ?)",
                       ("Смартфон", 30000, 2, "Новый смартфон"))

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                   (credentials.username, hash_password(credentials.password)))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )

    return User(id=user[0], username=user[1], role=user[2])


# API endpoints
@app.post("/register")
def register(username: str, password: str, role: str = "customer"):
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hash_password(password), role))
        conn.commit()
        return {"message": "Пользователь создан"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    finally:
        conn.close()


@app.get("/products", response_model=List[Product])
def get_products():
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, seller_id, description FROM products")
    products = [Product(id=row[0], name=row[1], price=row[2], seller_id=row[3], description=row[4])
                for row in cursor.fetchall()]
    conn.close()
    return products


@app.post("/products")
def create_product(name: str, price: float, description: str, user: User = Depends(get_current_user)):
    if user.role not in ['seller', 'admin']:
        raise HTTPException(status_code=403, detail="Только продавцы могут добавлять товары")

    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, seller_id, description) VALUES (?, ?, ?, ?)",
                   (name, price, user.id, description))
    conn.commit()
    conn.close()
    return {"message": "Товар добавлен"}


@app.post("/buy/{product_id}")
def buy_product(product_id: int, user: User = Depends(get_current_user)):
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()

    # Проверяем существование товара
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Создаем заказ
    cursor.execute("INSERT INTO orders (user_id, product_id, status) VALUES (?, ?, ?)",
                   (user.id, product_id, "paid"))  # В реальном приложении здесь была бы оплата
    conn.commit()
    conn.close()

    return {"message": "Заказ создан и оплачен"}


@app.get("/my-orders", response_model=List[Order])
def get_my_orders(user: User = Depends(get_current_user)):
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, product_id, status FROM orders WHERE user_id = ?", (user.id,))
    orders = [Order(id=row[0], user_id=row[1], product_id=row[2], status=row[3])
              for row in cursor.fetchall()]
    conn.close()
    return orders


@app.get("/")
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    init_db()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
