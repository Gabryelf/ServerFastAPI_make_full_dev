import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


from app.database import SessionLocal
from app.models import User


def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("=== USERS IN DATABASE ===")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Name: {user.full_name}")
        print(f"Total users: {len(users)}")
        print("=========================")
    finally:
        db.close()


if __name__ == "__main__":
    check_users()