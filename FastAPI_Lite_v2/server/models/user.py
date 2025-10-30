from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import hashlib
import secrets


class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(UserBase):
    id: int
    role: UserRole = UserRole.USER
    hashed_password: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UserPublic(UserBase):
    id: int
    role: UserRole
    is_active: bool


class UserManager:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        return f"{salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not hashed_password or '$' not in hashed_password:
            return False

        try:
            salt, hash_value = hashed_password.split('$')
            return hashlib.sha256((salt + plain_password).encode()).hexdigest() == hash_value
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def user_to_dict(user: UserInDB) -> Dict[str, Any]:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }