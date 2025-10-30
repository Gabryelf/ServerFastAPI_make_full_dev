const API_BASE = 'http://localhost:8000';
let currentUser = null;
let token = localStorage.getItem('token');

console.log("=== APP INIT ===");
console.log("Initial token:", token);

// Основная функция загрузки пользователя
async function loadCurrentUser() {
    console.log("🔄 Loading current user...");

    token = localStorage.getItem('token');
    console.log("Token from localStorage:", token);

    if (!token) {
        console.log("❌ No token found");
        currentUser = null;
        return null;
    }

    try {
        const response = await fetch(`${API_BASE}/api/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        console.log("User API response status:", response.status);

        if (response.ok) {
            currentUser = await response.json();
            console.log("✅ Current user loaded:", currentUser);
            return currentUser;
        } else {
            console.log("❌ Failed to load user, removing invalid token");
            localStorage.removeItem('token');
            token = null;
            currentUser = null;
            return null;
        }
    } catch (error) {
        console.error('❌ Load user error:', error);
        localStorage.removeItem('token');
        token = null;
        currentUser = null;
        return null;
    }
}

// Обновление навигации
function updateNavigation() {
    console.log("🔄 Updating navigation...");

    const authLinks = document.getElementById('auth-links');
    const userLinks = document.getElementById('user-links');
    const adminLinks = document.getElementById('admin-links');

    if (currentUser) {
        console.log("✅ User is authenticated, showing user links");
        if (authLinks) authLinks.style.display = 'none';
        if (userLinks) userLinks.style.display = 'flex';

        if (adminLinks && currentUser.role === 'admin') {
            adminLinks.style.display = 'block';
            console.log("👑 Admin links enabled");
        }

        const welcomeEl = document.getElementById('user-welcome');
        if (welcomeEl) {
            welcomeEl.textContent = `Добро пожаловать, ${currentUser.full_name}!`;
        }
    } else {
        console.log("❌ User is not authenticated, showing auth links");
        if (authLinks) authLinks.style.display = 'flex';
        if (userLinks) userLinks.style.display = 'none';
        if (adminLinks) adminLinks.style.display = 'none';
    }
}

// Выход из системы
function logout() {
    console.log("🚪 Logging out...");
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    showMessage('Вы вышли из системы', 'success');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

// Показать сообщение
function showMessage(message, type = 'success') {
    console.log(`Message (${type}): ${message}`);

    const messageEl = document.getElementById('auth-message') || document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.classList.remove('hidden');

        setTimeout(() => {
            messageEl.classList.add('hidden');
        }, 5000);
    } else {
        alert(`${type === 'success' ? '✅' : '❌'} ${message}`);
    }
}

// Функция для входа
async function loginUser(email, password) {
    console.log("🔐 Logging in user:", email);

    try {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        console.log("Login response status:", response.status);

        if (response.ok) {
            const loginData = await response.json();

            localStorage.setItem('token', loginData.access_token);
            token = loginData.access_token;
            console.log("✅ Login successful, token saved");

            showMessage('Вход выполнен! Перенаправляем...', 'success');

            // Сразу редирект, не ждем загрузку пользователя
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);

            return true;
        } else {
            const errorData = await response.json();
            console.error("❌ Login failed:", errorData);
            showMessage(errorData.detail || 'Ошибка входа', 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Login connection error:', error);
        showMessage('Ошибка соединения', 'error');
        return false;
    }
}

// Функция для регистрации
async function registerUser(fullName, email, password) {
    console.log("👤 Registering user:", email);

    try {
        const response = await fetch(`${API_BASE}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_name: fullName,
                email,
                password
            }),
        });

        console.log("Register response status:", response.status);

        if (response.ok) {
            console.log("✅ Registration successful");
            showMessage('Регистрация успешна! Выполняется вход...', 'success');

            // Сразу логинимся после регистрации
            const loginSuccess = await loginUser(email, password);
            return loginSuccess;
        } else {
            const errorData = await response.json();
            console.error("❌ Registration failed:", errorData);
            showMessage(errorData.detail || 'Ошибка регистрации', 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Register connection error:', error);
        showMessage('Ошибка соединения', 'error');
        return false;
    }
}

// Проверка авторизации для защищенных страниц
async function checkProtectedPageAccess() {
    console.log("🔐 Checking protected page access...");
    console.log("Current page:", window.location.pathname);

    // Только для защищенных страниц
    if (window.location.pathname.includes('dashboard.html') ||
        window.location.pathname.includes('admin.html')) {

        console.log("🛡️ This is a protected page, checking auth...");

        // Сначала пытаемся загрузить пользователя
        const user = await loadCurrentUser();

        if (!user) {
            console.log("❌ No user found, redirecting to login");
            showMessage('Для доступа необходимо войти в систему', 'error');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return false;
        }

        console.log("✅ Access granted for protected page");
        return true;
    }

    return true;
}

// Проверка редиректа для уже авторизованных пользователей
async function checkAuthRedirect() {
    console.log("🔄 Checking auth redirect...");

    // Если пользователь уже на dashboard, ничего не делаем
    if (window.location.pathname.includes('dashboard.html') ||
        window.location.pathname.includes('admin.html')) {
        return;
    }

    // Загружаем пользователя
    await loadCurrentUser();

    // Если пользователь авторизован и на странице входа/регистрации - редирект
    if (currentUser && (window.location.pathname.includes('login.html') ||
                        window.location.pathname.includes('register.html'))) {
        console.log("✅ User already authenticated, redirecting to dashboard");
        showMessage(`Вы уже вошли как ${currentUser.full_name}`, 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    }
}

// Инициализация форм входа/регистрации
function initializeAuthForms() {
    console.log("📝 Initializing auth forms...");

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        console.log("✅ Found login form");
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(e.target);
            const email = formData.get('email');
            const password = formData.get('password');

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Вход...';
            submitBtn.disabled = true;

            await loginUser(email, password);

            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }

    if (registerForm) {
        console.log("✅ Found register form");
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(e.target);
            const fullName = formData.get('full_name');
            const email = formData.get('email');
            const password = formData.get('password');
            const confirmPassword = formData.get('confirm_password');

            if (password !== confirmPassword) {
                showMessage('Пароли не совпадают', 'error');
                return;
            }

            if (password.length < 6) {
                showMessage('Пароль должен быть не менее 6 символов', 'error');
                return;
            }

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Регистрация...';
            submitBtn.disabled = true;

            await registerUser(fullName, email, password);

            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }
}

// Главная инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    console.log("=== PAGE LOADED ===");
    console.log("Current page:", window.location.pathname);

    // 1. Сначала инициализируем формы (если есть)
    initializeAuthForms();

    // 2. Проверяем доступ к защищенным страницам
    const hasAccess = await checkProtectedPageAccess();

    // 3. Если доступ есть или страница не защищенная - загружаем пользователя и обновляем навигацию
    if (hasAccess || !window.location.pathname.includes('dashboard.html')) {
        await loadCurrentUser();
        updateNavigation();
    }

    // 4. Проверяем редиректы для уже авторизованных
    await checkAuthRedirect();
});

// Глобальные функции
window.logout = logout;
window.showMessage = showMessage;