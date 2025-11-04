from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    role: str  # 'customer', 'seller', 'admin'


class Product(BaseModel):
    id: int
    name: str
    price: float
    seller_id: int
    description: str = ""


class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    status: str  # 'pending', 'paid', 'shipped'


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "customer"
