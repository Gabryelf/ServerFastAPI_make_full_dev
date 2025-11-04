from fastapi import HTTPException
from models import Order
from database import Database

db = Database()


class OrderService:
    def __init__(self):
        self.db = db

    def create_order(self, user_id: int, product_id: int) -> dict:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # ПРОВЕРКА ЗАКАЗА
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Товар не найден")

        # СОЗДАНИЕ ЗАКАЗА
        cursor.execute("INSERT INTO orders (user_id, product_id, status) VALUES (?, ?, ?)",
                       (user_id, product_id, "paid"))
        conn.commit()
        conn.close()

        return {"message": "Заказ создан и оплачен"}

    def get_user_orders(self, user_id: int) -> list[Order]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, product_id, status FROM orders WHERE user_id = ?", (user_id,))
        orders = [Order(id=row[0], user_id=row[1], product_id=row[2], status=row[3])
                  for row in cursor.fetchall()]
        conn.close()
        return orders


order_service = OrderService()
