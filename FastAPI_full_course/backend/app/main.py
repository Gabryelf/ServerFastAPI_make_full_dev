from fastapi import FastAPI
from .database import init_db
from .middleware.cors import setup_cors
from .routes import auth, users

init_db()

app = FastAPI(
    title="User Platform API",
    description="Backend для пользовательской платформы",
    version="1.0.0"
)

setup_cors(app)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "User Platform API", "status": "running"}