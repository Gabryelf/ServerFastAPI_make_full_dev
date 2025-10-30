from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path

from .database import get_db, init_db
from . import schemas
from .auth import get_current_user, authenticate_user
from .crud import get_user_by_email, create_user, get_products, get_product, create_product, update_product, \
    delete_product, make_user_admin, delete_user
from .models import User, Product
from .config import settings

# Initialize database
init_db()

app = FastAPI(title="Marketplace API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("app/static/uploads", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Определяем пути к фронтенду
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

print(f"Frontend directory: {FRONTEND_DIR}")
print(f"Frontend exists: {FRONTEND_DIR.exists()}")


# API routes - должны быть ДО catch-all маршрута
@app.get("/api/info")
async def get_server_info():
    return {
        "database_type": settings.DATABASE_TYPE,
        "status": "running"
    }


# Auth routes
@app.post("/api/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"=== REGISTRATION REQUEST ===")
        print(f"Email: {user.email}")
        print(f"Full name: {user.full_name}")

        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            print("❌ User already exists")
            raise HTTPException(status_code=400, detail="Email already registered")

        print("✅ Creating new user...")
        new_user = create_user(db=db, user=user)
        print(f"✅ User created successfully: {new_user.email}")
        return new_user

    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/login")
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    from .auth import create_access_token
    return create_access_token(user)


@app.get("/api/me", response_model=schemas.User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# Product routes
@app.post("/api/products/", response_model=schemas.Product)
async def create_product(
        name: str = Form(...),
        description: str = Form(...),
        images: List[UploadFile] = File(None),
        videos: List[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Validate file limits
    if images and len(images) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed")
    if videos and len(videos) > 2:
        raise HTTPException(status_code=400, detail="Maximum 2 videos allowed")

    image_paths = []
    video_paths = []

    # Save images
    if images:
        for image in images:
            file_extension = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"app/static/uploads/{filename}"

            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)

            image_paths.append(f"/static/uploads/{filename}")

    # Save videos
    if videos:
        for video in videos:
            file_extension = os.path.splitext(video.filename)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"app/static/uploads/{filename}"

            with open(file_path, "wb") as buffer:
                content = await video.read()
                buffer.write(content)

            video_paths.append(f"/static/uploads/{filename}")

    product_data = schemas.ProductCreate(
        name=name,
        description=description,
        image_paths=image_paths,
        video_paths=video_paths
    )

    return create_product(db=db, product=product_data, user_id=current_user.id)


@app.get("/api/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = get_products(db, skip=skip, limit=limit)
    return products


@app.get("/api/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/api/products/{product_id}", response_model=schemas.Product)
def update_product(
        product_id: int,
        product: schemas.ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_product = get_product(db, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if db_product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return update_product(db=db, product_id=product_id, product=product)


@app.delete("/api/products/{product_id}")
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_product = get_product(db, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if db_product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    delete_product(db=db, product_id=product_id)
    return {"message": "Product deleted successfully"}


# Admin routes
@app.post("/api/admin/users/{user_id}/make-admin")
def make_user_admin(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Only first admin can create other admins
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Only first admin can create other admins")

    return make_user_admin(db=db, user_id=user_id)


@app.delete("/api/admin/users/{user_id}")
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    return delete_user(db=db, user_id=user_id)


# Admin routes
@app.get("/api/admin/users")
def get_all_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    users = db.query(User).all()
    return users


@app.get("/api/admin/stats")
def get_admin_stats(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    total_admins = db.query(User).filter(User.role == "admin").count()

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_admins": total_admins
    }


# Debug endpoint
@app.get("/api/debug/db-check")
def debug_db_check(db: Session = Depends(get_db)):
    """Проверка подключения к базе данных"""
    try:
        from sqlalchemy import text
        # Проверяем подключение
        result = db.execute(text("SELECT 1"))
        db_check = result.scalar()

        # Проверяем таблицы
        result = db.execute(text("SHOW TABLES"))
        tables = [table[0] for table in result.fetchall()]

        # Проверяем пользователей
        users_count = db.query(User).count()

        return {
            "database_connection": "✅ OK" if db_check == 1 else "❌ FAILED",
            "tables": tables,
            "users_count": users_count,
            "database_url": settings.database_url
        }
    except Exception as e:
        return {
            "database_connection": "❌ FAILED",
            "error": str(e)
        }


# Serve frontend - ДОЛЖЕН БЫТЬ ПОСЛЕДНИМ
@app.get("/")
async def read_index():
    index_path = FRONTEND_DIR / "index.html"
    print(f"Serving index from: {index_path}")
    return FileResponse(str(index_path))


@app.get("/{path:path}")
async def serve_frontend(path: str):
    # Сначала проверяем, не является ли путь API маршрутом
    if path.startswith('api/'):
        # Если это API маршрут, который не был обработан выше, возвращаем 404
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # Пытаемся найти файл во фронтенде
    frontend_path = FRONTEND_DIR / path

    print(f"Looking for: {frontend_path}")
    print(f"Exists: {frontend_path.exists()}")

    if frontend_path.exists() and frontend_path.is_file():
        print(f"Serving: {frontend_path}")
        return FileResponse(str(frontend_path))

    # Для SPA маршрутов возвращаем index.html
    print(f"SPA route, serving index.html for: {path}")
    return FileResponse(str(FRONTEND_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)