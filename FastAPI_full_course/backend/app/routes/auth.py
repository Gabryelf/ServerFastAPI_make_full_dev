from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..database import get_db
from ..auth.security import (
    verify_password, get_password_hash, create_access_token,
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..models.user import UserCreate, User, UserRole, UserStatus, Token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?", (payload.get("sub"),)
        ).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return User(**dict(user))


@router.post("/register", response_model=User)
def register(user_data: UserCreate):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user_data.username, user_data.email)
        ).fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="Username or email already exists")

        hashed_password = get_password_hash(user_data.password)
        cursor = conn.execute('''
            INSERT INTO users (username, email, full_name, hashed_password, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_data.username, user_data.email, user_data.full_name,
            hashed_password, UserRole.USER, UserStatus.BASIC
        ))

        user_id = cursor.lastrowid
        conn.commit()

        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    return User(**dict(user))


@router.post("/login", response_model=Token)
def login(username: str, password: str):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(**dict(user))
    }
