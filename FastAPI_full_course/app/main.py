from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from app.backend import router as backend_router
from app.frontend import router as frontend_router

app = FastAPI(title="My Student Service", version="1.0.0")

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
static_dir = os.path.join(project_root, "static")

if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(backend_router)
app.include_router(frontend_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
