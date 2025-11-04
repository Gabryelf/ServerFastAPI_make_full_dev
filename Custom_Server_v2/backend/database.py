import sqlite3
import hashlib


class Database:
    def __init__(self, db_name='marketplace.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')

        # Таблица товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                seller_id INTEGER,
                description TEXT
            )
        ''')

        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                status TEXT
            )
        ''')

        # ДАННЫЕ ДЛЯ ТЕСТОВ
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self._create_test_data(cursor)

        conn.commit()
        conn.close()

    def _create_test_data(self, cursor):
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("admin", self.hash_password("admin"), "admin"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("seller1", self.hash_password("123"), "seller"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("customer1", self.hash_password("123"), "customer"))

        cursor.execute("INSERT INTO products (name, price, seller_id, description) VALUES (?, ?, ?, ?)",
                       ("Ноутбук", 50000, 2, "Мощный игровой ноутбук"))
        cursor.execute("INSERT INTO products (name, price, seller_id, description) VALUES (?, ?, ?, ?)",
                       ("Смартфон", 30000, 2, "Новый смартфон"))

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()