// Глобальные переменные для админки
let allUsers = [];
let allProducts = [];
let currentAction = null;
let currentItemId = null;

// Инициализация админ панели
document.addEventListener('DOMContentLoaded', async () => {
    // Проверяем права доступа
    await checkAdminAccess();

    // Загружаем данные
    await loadAdminData();

    // Настраиваем поиск
    setupSearch();
});

// Проверка прав администратора
async function checkAdminAccess() {
    await loadCurrentUser();

    if (!currentUser || currentUser.role !== 'admin') {
        alert('Доступ запрещен. Требуются права администратора.');
        window.location.href = 'index.html';
        return;
    }
}

// Загрузка всех данных для админки
async function loadAdminData() {
    try {
        await Promise.all([
            loadUsers(),
            loadAllProductsForAdmin(),
            updateStats()
        ]);
    } catch (error) {
        console.error('Error loading admin data:', error);
        showMessage('Ошибка загрузки данных', 'error');
    }
}

// Загрузка списка пользователей
async function loadUsers() {
    try {
        // В реальном приложении здесь был бы endpoint /api/admin/users
        // Пока используем существующие endpoints и фильтруем
        const productsResponse = await fetch(`${API_BASE}/api/products/`);
        const allProducts = await productsResponse.json();

        // Собираем уникальных пользователей из товаров
        const usersMap = new Map();

        // Добавляем текущего пользователя (админа)
        usersMap.set(currentUser.id, {
            id: currentUser.id,
            email: currentUser.email,
            full_name: currentUser.full_name,
            role: currentUser.role,
            products_count: allProducts.filter(p => p.owner_id === currentUser.id).length
        });

        // Добавляем остальных пользователей из товаров
        allProducts.forEach(product => {
            if (!usersMap.has(product.owner_id)) {
                usersMap.set(product.owner_id, {
                    id: product.owner_id,
                    email: product.owner_email || 'unknown@example.com',
                    full_name: product.owner_name || 'Неизвестный пользователь',
                    role: 'user', // По умолчанию считаем обычным пользователем
                    products_count: allProducts.filter(p => p.owner_id === product.owner_id).length
                });
            }
        });

        allUsers = Array.from(usersMap.values());
        displayUsers(allUsers);

    } catch (error) {
        console.error('Error loading users:', error);
        showMessage('Ошибка загрузки пользователей', 'error');
    }
}

// Отображение пользователей
function displayUsers(users) {
    const container = document.getElementById('users-list');

    if (users.length === 0) {
        container.innerHTML = '<div class="empty-state">Пользователи не найдены</div>';
        return;
    }

    container.innerHTML = users.map(user => `
        <div class="user-card admin-card">
            <div class="user-info">
                <div class="user-avatar">
                    ${user.full_name.charAt(0).toUpperCase()}
                </div>
                <div class="user-details">
                    <h4>${user.full_name}</h4>
                    <p class="user-email">${user.email}</p>
                    <div class="user-stats">
                        <span class="badge ${user.role === 'admin' ? 'badge-warning' : 'badge-info'}">
                            ${user.role === 'admin' ? '👑 Админ' : '👤 Пользователь'}
                        </span>
                        <span class="badge badge-secondary">
                            📦 Товаров: ${user.products_count || 0}
                        </span>
                    </div>
                </div>
            </div>
            <div class="user-actions">
                ${user.id !== currentUser.id ? `
                    ${user.role !== 'admin' ? `
                        <button onclick="promoteToAdmin(${user.id})"
                                class="btn btn-success btn-small">
                            Сделать админом
                        </button>
                    ` : ''}
                    <button onclick="confirmDeleteUser(${user.id})"
                            class="btn btn-danger btn-small">
                        Удалить
                    </button>
                ` : `
                    <span class="current-user-badge">Это вы</span>
                `}
            </div>
        </div>
    `).join('');
}

// Загрузка всех товаров для админки
async function loadAllProductsForAdmin() {
    try {
        const response = await fetch(`${API_BASE}/api/products/`);
        allProducts = await response.json();
        displayAllProducts(allProducts);
    } catch (error) {
        console.error('Error loading products for admin:', error);
        showMessage('Ошибка загрузки товаров', 'error');
    }
}

// Отображение всех товаров в админке
function displayAllProducts(products) {
    const grid = document.getElementById('admin-products-grid');

    if (products.length === 0) {
        grid.innerHTML = '<div class="empty-state">Товары не найдены</div>';
        return;
    }

    grid.innerHTML = products.map(product => {
        const firstImage = product.image_paths && product.image_paths.length > 0
            ? product.image_paths[0]
            : '/static/uploads/default-product.jpg';

        return `
            <div class="product-card admin-product-card">
                <img src="${API_BASE}${firstImage}" alt="${product.name}" class="product-image"
                     onerror="this.src='${API_BASE}/static/uploads/default-product.jpg'">
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-description">${product.description}</p>
                    <div class="product-meta">
                        <span class="product-owner">Владелец: ${product.owner_name || 'Неизвестно'}</span>
                        <span class="product-images-count">
                            📷 ${product.image_paths ? product.image_paths.length : 0} фото
                            ${product.video_paths ? `🎥 ${product.video_paths.length} видео` : ''}
                        </span>
                    </div>
                    <div class="product-actions">
                        <button onclick="viewProductDetail(${product.id})"
                                class="btn btn-outline btn-small">
                            Просмотр
                        </button>
                        <button onclick="confirmDeleteProduct(${product.id})"
                                class="btn btn-danger btn-small">
                            Удалить
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Обновление статистики
function updateStats() {
    document.getElementById('total-users').textContent = allUsers.length;
    document.getElementById('total-products').textContent = allProducts.length;
    document.getElementById('total-admins').textContent = allUsers.filter(u => u.role === 'admin').length;
}

// Назначение пользователя администратором
async function promoteToAdmin(userId) {
    if (!confirm(`Назначить этого пользователя администратором?`)) return;

    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}/make-admin`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showMessage('Пользователь назначен администратором', 'success');
            // Обновляем данные
            await loadAdminData();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка назначения администратора', 'error');
        }
    } catch (error) {
        console.error('Promote to admin error:', error);
        showMessage('Ошибка соединения', 'error');
    }
}

// Подтверждение удаления пользователя
function confirmDeleteUser(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (!user) return;

    currentAction = 'deleteUser';
    currentItemId = userId;

    document.getElementById('confirm-message').textContent =
        `Вы уверены, что хотите удалить пользователя "${user.full_name}" (${user.email})? Будут также удалены все его товары.`;

    showModal('confirm-modal');
}

// Подтверждение удаления товара
function confirmDeleteProduct(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;

    currentAction = 'deleteProduct';
    currentItemId = productId;

    document.getElementById('confirm-message').textContent =
        `Вы уверены, что хотите удалить товар "${product.name}"?`;

    showModal('confirm-modal');
}

// Обработчик подтвержденного действия
document.getElementById('confirm-action').addEventListener('click', async () => {
    hideModal('confirm-modal');

    switch (currentAction) {
        case 'deleteUser':
            await deleteUser(currentItemId);
            break;
        case 'deleteProduct':
            await deleteProductAdmin(currentItemId);
            break;
    }

    currentAction = null;
    currentItemId = null;
});

// Удаление пользователя (админская версия)
async function deleteUser(userId) {
    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showMessage('Пользователь и его товары удалены', 'success');
            await loadAdminData();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка удаления пользователя', 'error');
        }
    } catch (error) {
        console.error('Delete user error:', error);
        showMessage('Ошибка соединения', 'error');
    }
}

// Удаление товара (админская версия)
async function deleteProductAdmin(productId) {
    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showMessage('Товар удален', 'success');
            await loadAdminData();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка удаления товара', 'error');
        }
    } catch (error) {
        console.error('Delete product error:', error);
        showMessage('Ошибка соединения', 'error');
    }
}

// Система вкладок
function openTab(tabName) {
    // Скрываем все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Убираем активный класс у всех кнопок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Показываем выбранную вкладку
    document.getElementById(tabName).classList.add('active');

    // Активируем кнопку
    event.currentTarget.classList.add('active');
}

// Настройка поиска
function setupSearch() {
    const userSearch = document.getElementById('user-search');
    const productSearch = document.getElementById('product-search');

    if (userSearch) {
        userSearch.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const filteredUsers = allUsers.filter(user =>
                user.full_name.toLowerCase().includes(searchTerm) ||
                user.email.toLowerCase().includes(searchTerm)
            );
            displayUsers(filteredUsers);
        });
    }

    if (productSearch) {
        productSearch.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const filteredProducts = allProducts.filter(product =>
                product.name.toLowerCase().includes(searchTerm) ||
                product.description.toLowerCase().includes(searchTerm)
            );
            displayAllProducts(filteredProducts);
        });
    }
}

// Просмотр деталей товара
function viewProductDetail(productId) {
    window.open(`product-detail.html?id=${productId}`, '_blank');
}
