from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/api", tags=["backend"])


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float


fake_items_db = []


@router.post("/items/")
async def create_item(item: Item):
    fake_items_db.append(item)
    return {"message": "Item created successfully", "item": item}


@router.get("/items/")
async def read_items():
    return fake_items_db


@router.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0 or item_id >= len(fake_items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]

