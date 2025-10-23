from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def read_index():
    return """
    <html>
        <head>
            <title>My Student Service</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <h1>Welcome to Our Service!</h1>
            <p>This is our main page. Backend API is <a href="/docs">here</a>.</p>
        </body>
    </html>
    """