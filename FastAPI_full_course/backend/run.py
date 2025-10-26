from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Backend Server starting...")
    print("http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
