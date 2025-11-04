from models import Product
from database import Database

db = Database()


class ProductService:
    def __init__(self):
        self.db = db

    def get_all_products(self) -> list[Product]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, seller_id, description FROM products")
        products = [Product(id=row[0], name=row[1], price=row[2], seller_id=row[3], description=row[4])
                    for row in cursor.fetchall()]
        conn.close()
        return products

    def create_product(self, name: str, price: float, description: str, seller_id: int) -> dict:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, seller_id, description) VALUES (?, ?, ?, ?)",
                       (name, price, seller_id, description))
        conn.commit()
        conn.close()
        return {"message": "Товар добавлен"}


product_service = ProductService()
