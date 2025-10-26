// Главные функции приложения
function showPage(pageName) {
    // Скрываем все страницы
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Показываем выбранную страницу
    document.getElementById(`${pageName}-page`).classList.add('active');

    // Загружаем данные если нужно
    if (pageName === 'users') {
        loadAllUsers();
    } else if (pageName === 'dashboard' && token) {
        loadDashboard();
    }
}

async function loadAllUsers() {
    try {
        const response = await fetch(`${API_BASE}/users/`);
        if (response.ok) {
            const users = await response.json();
            displayUsers(users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function displayUsers(users) {
    const container = document.getElementById('users-list');
    container.innerHTML = users.map(user => `
        <div class="user-card" onclick="showUserProfile(${user.id})">
            <h3>${user.username}</h3>
            <p>${user.full_name || 'Не указано'}</p>
            <p>Email: ${user.email}</p>
            <span class="status-badge status-${user.status}">${user.status}</span>
            <p>Товаров: ${user.items_count}</p>
        </div>
    `).join('');
}

async function showUserProfile(userId) {
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`);
        if (response.ok) {
            const user = await response.json();
            document.getElementById('profile-content').innerHTML = `
                <div class="user-card">
                    <h2>${user.username}</h2>
                    <p>${user.full_name || 'Не указано'}</p>
                    <p>Email: ${user.email}</p>
                    <span class="status-badge status-${user.status}">${user.status}</span>
                    <p>Товаров: ${user.items_count}</p>
                </div>
            `;

            // Загружаем товары пользователя
            const itemsResponse = await fetch(`${API_BASE}/users/${userId}/items`);
            if (itemsResponse.ok) {
                const items = await itemsResponse.json();
                displayItems(items, 'user-items');
            }

            showPage('profile');
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

async function loadDashboard() {
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-info').innerHTML = `
                <div class="user-info">
                    <h3>${currentUser.username}</h3>
                    <p>${currentUser.full_name || 'Не указано'}</p>
                    <p>Email: ${currentUser.email}</p>
                    <span class="status-badge status-${currentUser.status}">${currentUser.status}</span>
                    <p>Товаров: ${currentUser.items_count}</p>
                    ${currentUser.status === 'basic' ? `<p>⚠️ Лимит: ${5 - currentUser.items_count}/5 товаров</p>` : ''}
                </div>
            `;
            updateAuthUI();
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
    if (token) {
        loadDashboard();
    }
});