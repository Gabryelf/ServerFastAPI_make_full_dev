const API_BASE = 'http://localhost:8000';
let currentUser = null;
let token = null;

// Auth functions
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            await loadCurrentUser();
            hideModals();
            loadProducts();
            updateUI();
        } else {
            alert('Ошибка входа');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Ошибка входа');
    }
}

async function register(fullName, email, password) {
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ full_name: fullName, email, password }),
        });

        if (response.ok) {
            alert('Регистрация успешна! Теперь войдите в систему.');
            hideModals();
            showLogin();
        } else {
            const error = await response.json();
            alert(error.detail || 'Ошибка регистрации');
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('Ошибка регистрации');
    }
}

async function loadCurrentUser() {
    token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE}/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            currentUser = await response.json();
        } else {
            localStorage.removeItem('token');
            token = null;
        }
    } catch (error) {
        console.error('Load user error:', error);
        localStorage.removeItem('token');
        token = null;
    }
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    updateUI();
    loadProducts();
}

// Product functions
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/`);
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Load products error:', error);
    }
}

function displayProducts(products) {
    const container = document.getElementById('products-list');
    container.innerHTML = '';

    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';

        let imagesHTML = '';
        if (product.image_paths && product.image_paths.length > 0) {
            imagesHTML = `
                <div class="product-images">
                    ${product.image_paths.map(path =>
                        `<img src="${API_BASE}${path}" alt="Product image">`
                    ).join('')}
                </div>
            `;
        }

        let videosHTML = '';
        if (product.video_paths && product.video_paths.length > 0) {
            videosHTML = `
                <div class="product-videos">
                    ${product.video_paths.map(path =>
                        `<video controls>
                            <source src="${API_BASE}${path}" type="video/mp4">
                            Ваш браузер не поддерживает видео.
                        </video>`
                    ).join('')}
                </div>
            `;
        }

        let actionsHTML = '';
        if (currentUser && (currentUser.role === 'admin' || currentUser.id === product.owner_id)) {
            actionsHTML = `
                <div class="product-actions">
                    <button class="edit-btn" onclick="editProduct(${product.id})">Редактировать</button>
                    <button class="delete-btn" onclick="deleteProduct(${product.id})">Удалить</button>
                </div>
            `;
        }

        productCard.innerHTML = `
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            ${imagesHTML}
            ${videosHTML}
            ${actionsHTML}
        `;

        container.appendChild(productCard);
    });
}

async function createProduct(formData) {
    try {
        const response = await fetch(`${API_BASE}/products/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData,
        });

        if (response.ok) {
            hideModals();
            loadProducts();
        } else {
            alert('Ошибка создания товара');
        }
    } catch (error) {
        console.error('Create product error:', error);
        alert('Ошибка создания товара');
    }
}

async function deleteProduct(productId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) return;

    try {
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            loadProducts();
        } else {
            alert('Ошибка удаления товара');
        }
    } catch (error) {
        console.error('Delete product error:', error);
        alert('Ошибка удаления товара');
    }
}

// Admin functions
async function loadUsers() {
    // In a real app, you'd have an endpoint to get all users
    // For now, we'll just show a message
    document.getElementById('users-list').innerHTML = '<p>Функционал управления пользователями будет реализован позже</p>';
}

// UI functions
function showLogin() {
    hideModals();
    document.getElementById('login-modal').style.display = 'block';
}

function showRegister() {
    hideModals();
    document.getElementById('register-modal').style.display = 'block';
}

function showCreateProduct() {
    hideModals();
    document.getElementById('create-product-modal').style.display = 'block';
}

function showAdminPanel() {
    document.getElementById('admin-panel').style.display = 'block';
    document.getElementById('products-container').style.display = 'none';
    loadUsers();
}

function hideModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

function updateUI() {
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userInfo = document.getElementById('user-info');
    const createProductBtn = document.getElementById('create-product-btn');
    const adminPanelBtn = document.getElementById('admin-panel-btn');

    if (currentUser) {
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
        userInfo.style.display = 'inline-block';
        userInfo.textContent = `${currentUser.full_name} (${currentUser.role})`;

        createProductBtn.style.display = 'inline-block';

        if (currentUser.role === 'admin') {
            adminPanelBtn.style.display = 'inline-block';
        } else {
            adminPanelBtn.style.display = 'none';
            document.getElementById('admin-panel').style.display = 'none';
            document.getElementById('products-container').style.display = 'block';
        }
    } else {
        loginBtn.style.display = 'inline-block';
        registerBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
        userInfo.style.display = 'none';
        createProductBtn.style.display = 'none';
        adminPanelBtn.style.display = 'none';
    }
}

async function loadServerInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/info`);
        const info = await response.json();
        console.log(`Server running with ${info.database_type} database`);
    } catch (error) {
        console.error('Failed to load server info:', error);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    await loadServerInfo();
    await loadCurrentUser();
    updateUI();
    loadProducts();

    // Login form
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const email = e.target[0].value;
        const password = e.target[1].value;
        login(email, password);
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const fullName = e.target[0].value;
        const email = e.target[1].value;
        const password = e.target[2].value;
        register(fullName, email, password);
    });

    // Create product form
    document.getElementById('create-product-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('name', e.target[0].value);
        formData.append('description', e.target[1].value);

        const imagesInput = document.getElementById('product-images');
        const videosInput = document.getElementById('product-videos');

        for (let i = 0; i < imagesInput.files.length; i++) {
            formData.append('images', imagesInput.files[i]);
        }

        for (let i = 0; i < videosInput.files.length; i++) {
            formData.append('videos', videosInput.files[i]);
        }

        createProduct(formData);
    });


});

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        hideModals();
    }
});