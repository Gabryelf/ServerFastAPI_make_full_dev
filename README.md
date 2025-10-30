# ServerFastAPI_make_full_dev
Курс по созданию сервера back & front на фреймворке FastAPI для Python3 с database & docker
# 🛍️ Marketplace Tutorial

<div align="center">

![Marketplace Demo](https://img.shields.io/badge/Marketplace-Tutorial-blue?style=for-the-badge&logo=shopping-cart)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green?style=for-the-badge&logo=fastapi)
![Vanilla JS](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=for-the-badge&logo=javascript)

**A step-by-step tutorial for building a modern marketplace with FastAPI and vanilla JavaScript**

[![Demo](https://img.shields.io/badge/🎯-Live_Demo-orange?style=for-the-badge)](https://your-demo-link.com)
[![Tutorial](https://img.shields.io/badge/📚-Step_by_Step_Guide-purple?style=for-the-badge)](#-tutorial-steps)
[![Code](https://img.shields.io/badge/💻-Source_Code-lightgrey?style=for-the-badge)](#-quick-start)

</div>

## ✨ Features

<div align="center">

| 🎯 Feature | 📱 Frontend | 🔧 Backend |
|-----------|-------------|------------|
| **User Authentication** | ✅ JWT Tokens | ✅ Secure Hashing |
| **Product Management** | ✅ CRUD Operations | ✅ File Upload |
| **Admin Panel** | ✅ User Management | ✅ Role-based Access |
| **Responsive Design** | ✅ Mobile Friendly | ✅ REST API |

</div>

## 🎬 Demo Preview

<div align="center">

![Marketplace Flow](https://via.placeholder.com/800x400/4F46E5/FFFFFF?text=Marketplace+Application+Demo)

</div>

## 🚀 Quick Start

### Prerequisites

```bash
# Backend Requirements
python >= 3.8
fastapi >= 0.104.0
sqlalchemy >= 2.0.0

# Frontend Requirements
modern web browser
local server (for CORS)
Installation
bash
# 1. Clone the repository
git clone https://github.com/your-username/marketplace-tutorial.git
cd marketplace-tutorial

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Run the backend server
uvicorn app.main:app --reload --port 8000

# 4. Open frontend in browser
# Navigate to frontend/ directory and open index.html
📚 Tutorial Steps
🎯 Step 1: Project Setup & Structure
<details> <summary>📁 Click to expand</summary>
text
marketplace-tutorial/
├── 📁 backend/
│   ├── 🐍 app/
│   │   ├── 🗄️  models.py
│   │   ├── 🔐 auth.py
│   │   ├── 🛠️  crud.py
│   │   └── 📋 schemas.py
│   └── 🚀 main.py
├── 📁 frontend/
│   ├── 🎨 css/
│   ├── ⚡ js/
│   └── 📄 *.html
└── 📖 README.md
Key Concepts:

MVC Architecture

RESTful API Design

JWT Authentication

</details>
🔐 Step 2: Authentication System
<details> <summary>🔑 Click to expand</summary>
python
# Backend JWT Implementation
@app.post("/api/login")
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
javascript
// Frontend Auth Management
async function loginUser(email, password) {
    const response = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email, password }),
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        showMessage('Welcome back! 🎉', 'success');
    }
}
Features:

Secure Password Hashing

JWT Token Management

Protected Routes

</details>
🛍️ Step 3: Product Management
<details> <summary>📦 Click to expand</summary>
python
# Backend Product CRUD
@app.post("/api/products/")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    # File handling and product creation logic
    product_data = schemas.ProductCreate(
        name=name,
        description=description,
        image_paths=processed_images
    )
    return crud.create_product(db, product_data, current_user.id)
javascript
// Frontend Product Creation
async function createProduct(formData) {
    const response = await fetch(`${API_BASE}/api/products/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData,
    });
    
    if (response.ok) {
        showMessage('Product created successfully! 🎉', 'success');
        loadMyProducts();
    }
}
Features:

Multi-file Upload

Image & Video Support

Real-time Updates

</details>
👑 Step 4: Admin Panel
<details> <summary>⚡ Click to expand</summary>
python
# Role-based Access Control
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
javascript
// Admin Features
if (currentUser.role === 'admin') {
    showAdminPanel();
    loadUserManagement();
}
Features:

User Management

Product Moderation

Analytics Dashboard

</details>
🎨 UI Components
Modern Design System
css
/* CSS Variables for Consistent Styling */
:root {
    --primary-color: #4F46E5;
    --success-color: #10B981;
    --danger-color: #EF4444;
    --border-radius: 12px;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Responsive Grid Layout */
.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1rem;
}
🔧 API Endpoints
Method	Endpoint	Description	Auth Required
POST	/api/register	User Registration	❌
POST	/api/login	User Login	❌
GET	/api/me	Get Current User	✅
GET	/api/products	List Products	❌
POST	/api/products	Create Product	✅
DELETE	/api/products/{id}	Delete Product	✅
🐛 Debugging Guide
Common Issues & Solutions
<details> <summary>🔍 CORS Issues</summary>
python
# Backend CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
</details><details> <summary>🔍 File Upload Problems</summary>
javascript
// Correct FormData Usage
const formData = new FormData();
formData.append('name', productName);
formData.append('images', imageFile); // Multiple files supported
// Don't set Content-Type header manually!
</details><details> <summary>🔍 JWT Token Issues</summary>
javascript
// Token Management
const token = localStorage.getItem('token');
if (!token) {
    redirectToLogin();
    return;
}
// Include token in Authorization header
headers: {'Authorization': `Bearer ${token}`}
</details>
📱 Responsive Design
<div align="center">
Device	Layout	Features
Desktop	Multi-column Grid	Full Admin Panel
Tablet	Adaptive Grid	All CRUD Operations
Mobile	Single Column	Touch-friendly UI
</div>
🚀 Deployment
Backend Deployment
bash
# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Environment variables
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
Frontend Deployment
Serve static files via Nginx/Apache

Configure CORS for your domain

Set up HTTPS for security

🤝 Contributing
We welcome contributions! Please see our Contributing Guide for details.

🍴 Fork the repository

🌿 Create a feature branch

💻 Make your changes

✅ Add tests

📦 Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE.md file for details.

🎯 Learning Path
<div align="center">
🏆 Skills You'll Learn
Week	Topic	Level
1	FastAPI Fundamentals	🟢 Beginner
2	JWT Authentication	🟡 Intermediate
3	File Upload Handling	🟡 Intermediate
4	Frontend-Backend Integration	🔴 Advanced
</div>
<div align="center">
🎊 Congratulations!
You've built a full-stack marketplace application! 🎉

Next Steps:

Add payment integration

Implement real-time chat

Deploy to cloud platform

Add advanced search filters

Made with ❤️ by the Marketplace Tutorial Team

</div> ```
