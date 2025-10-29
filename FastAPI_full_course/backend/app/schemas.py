from pydantic import BaseModel, EmailStr
from typing import List


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: str


class ProductCreate(ProductBase):
    image_paths: List[str] = []
    video_paths: List[str] = []


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    owner_id: int
    image_paths: List[str]
    video_paths: List[str]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
