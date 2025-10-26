from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..database import get_db
from ..models.user import User, Item, ItemCreate, UserStatus
from ..routes.auth import get_current_user
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

MAX_BASIC_ITEMS = 5


@router.get("/me", response_model=User)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[User])
def get_all_users():
    with get_db() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    return [User(**dict(user)) for user in users]


@router.get("/{user_id}", response_model=User)
def get_user_profile(user_id: int):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return User(**dict(user))


@router.post("/items", response_model=Item)
async def create_item(
        item_data: ItemCreate,
        image: UploadFile = File(None),
        current_user: User = Depends(get_current_user)
):
    if current_user.status == UserStatus.BASIC and current_user.items_count >= MAX_BASIC_ITEMS:
        raise HTTPException(
            status_code=400,
            detail=f"Basic users can only create {MAX_BASIC_ITEMS} items"
        )

    image_data = None
    if image:
        image_data = await image.read()
        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO items (title, description, image_data, owner_id)
            VALUES (?, ?, ?, ?)
        ''', (item_data.title, item_data.description, image_data, current_user.id))

        item_id = cursor.lastrowid
        conn.execute(
            "UPDATE users SET items_count = items_count + 1 WHERE id = ?",
            (current_user.id,)
        )
        conn.commit()

        item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    return Item(**dict(item))


@router.get("/{user_id}/items", response_model=List[Item])
def get_user_items(user_id: int):
    with get_db() as conn:
        items = conn.execute(
            "SELECT * FROM items WHERE owner_id = ?", (user_id,)
        ).fetchall()

    return [Item(**dict(item)) for item in items]


@router.get("/items/{item_id}/image")
def get_item_image(item_id: int):
    with get_db() as conn:
        item = conn.execute(
            "SELECT image_data FROM items WHERE id = ?", (item_id,)
        ).fetchone()

    if not item or not item["image_data"]:
        raise HTTPException(status_code=404, detail="Image not found")

    return item["image_data"]