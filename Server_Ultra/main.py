from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Simple FastAPI Demo", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

users_db = []
next_id = 1


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/users", response_model=List[User])
async def get_all_users():
    return users_db


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users")
async def create_user(user: User):
    global next_id
    user_data = user.model_dump()
    user_data["id"] = next_id
    users_db.append(user_data)
    next_id += 1
    return user_data


@app.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: User):
    for user in users_db:
        if user["id"] == user_id:
            user.update(updated_user.model_dump())
            user["id"] = user_id
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            deleted_user = users_db.pop(i)
            return {"message": f"User {deleted_user['name']} deleted"}
    raise HTTPException(status_code=404, detail="User not found")


# uvicorn main:app --reload --host 0.0.0.0 --port 8000
# pip install fastapi uvicorn jinja2 python-multipart
# http://localhost:8000
