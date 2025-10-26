const API_BASE = 'http://localhost:8000';

let currentUser = null;
let token = localStorage.getItem('token');

// Функции аутентификации
async function registerUser(event) {
    event.preventDefault();

    const userData = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        full_name: document.getElementById('reg-fullname').value,
        password: document.getElementById('reg-password').value
    };

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            alert('Регистрация успешна! Теперь войдите в систему.');
            showPage('login');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        alert('Ошибка соединения');
    }
}

async function loginUser(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            currentUser = data.user;

            localStorage.setItem('token', token);
            updateAuthUI();
            showPage('dashboard');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        alert('Ошибка соединения');
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    updateAuthUI();
    showPage('home');
}

function updateAuthUI() {
    const authSection = document.getElementById('authSection');

    if (token && currentUser) {
        authSection.innerHTML = `
            <span>Привет, ${currentUser.username}!</span>
            <a href="#" onclick="showPage('dashboard')">Кабинет</a>
            <a href="#" onclick="logout()">Выйти</a>
        `;
    } else {
        authSection.innerHTML = `
            <a href="#" onclick="showPage('login')">Войти</a>
            <a href="#" onclick="showPage('register')">Регистрация</a>
        `;
    }
}