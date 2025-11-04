import sqlite3
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models import User, UserCreate
from database import Database

security = HTTPBasic()
db = Database()


class AuthService:
    def __init__(self):
        self.db = db

    def get_current_user(self, credentials: HTTPBasicCredentials = Depends(security)) -> User:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                       (credentials.username, self.db.hash_password(credentials.password)))
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные"
            )

        return User(id=user_data[0], username=user_data[1], role=user_data[2])

    def register_user(self, user_data: UserCreate) -> dict:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (user_data.username, self.db.hash_password(user_data.password), user_data.role))
            conn.commit()
            return {"message": "Пользователь создан"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        finally:
            conn.close()


auth_service = AuthService()
