from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import traceback

from config import settings
from client.main import MarketplaceClient
from database.base import DatabaseManager
from database.mysql_adapter import MySQLAdapter
from repositories.user_repository import UserRepository
from models.user import UserCreate, UserLogin

client = MarketplaceClient()
db_manager = DatabaseManager()
user_repo = None


@asynccontextmanager
async def lifespan(main: FastAPI):
    print("Starting Marketplace server...")
    print(f"Connecting to MySQL database: {settings.DB_NAME}")

    try:
        db_adapter = MySQLAdapter(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )

        if await db_manager.initialize(db_adapter):
            global user_repo
            user_repo = UserRepository(db_manager)
            await user_repo.initialize()

            user_count = await user_repo.get_user_count()
            print(f"Database initialized with {user_count} users")

        else:
            print("Database initialization failed - please check MySQL connection")
            raise RuntimeError("Database connection failed")

    except Exception as e:
        print(f"Server startup error: {e}")
        traceback.print_exc()
        print("Check if MySQL is running and database exists")
        raise

    print(f"Marketplace server initialized on port {settings.PORT}")
    yield

    # Shutdown
    await db_manager.close()
    print("Shutting down Marketplace server...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


async def get_user_repository():
    if user_repo is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return user_repo


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("lobby.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/register")
async def register_user(
        user_data: UserCreate,
        user_repo: UserRepository = Depends(get_user_repository)
):

    try:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

        existing_username = await user_repo.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")

        user = await user_repo.create(user_data)
        if user:
            return {
                "message": "Пользователь успешно создан",
                "user_id": user.id,
                "username": user.username
            }
        else:
            print(f"Failed to create user: {user_data.username}")
            raise HTTPException(status_code=500, detail="Ошибка при создании пользователя")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error during registration: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/api/login")
async def login_user(
        login_data: UserLogin,
        user_repo: UserRepository = Depends(get_user_repository)
):
    print(f"Login attempt for: {login_data.email}")

    try:
        user = await user_repo.authenticate(login_data.email, login_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Неверные email или пароль")

        if not user.is_active:
            raise HTTPException(status_code=401, detail="Аккаунт деактивирован")

        return {
            "message": "Вход выполнен успешно",
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error during login: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/api/users")
async def get_users(user_repo: UserRepository = Depends(get_user_repository)):
    try:
        users = await user_repo.get_all()
        return {
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "role": u.role,
                    "email": u.email
                } for u in users
            ]
        }
    except Exception as e:
        print(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении пользователей")


@app.get("/api/debug/users")
async def debug_users(user_repo: UserRepository = Depends(get_user_repository)):
    try:
        users = await user_repo.get_all()
        user_data = []
        for user in users:
            user_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "hashed_password": user.hashed_password[:20] + "..." if user.hashed_password else None,
                "created_at": str(user.created_at),
                "updated_at": str(user.updated_at)
            })

        return {
            "total_users": len(users),
            "users": user_data
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
