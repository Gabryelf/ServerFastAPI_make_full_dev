// Обработчик регистрации
async function handleRegister(e) {
    e.preventDefault();
    console.log("=== REGISTRATION STARTED ===");

    const formData = new FormData(e.target);
    const fullName = formData.get('full_name');
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');

    // Валидация пароля
    if (password !== confirmPassword) {
        showMessage('Пароли не совпадают', 'error');
        return;
    }

    if (password.length < 6) {
        showMessage('Пароль должен быть не менее 6 символов', 'error');
        return;
    }

    console.log("Registration data:", { fullName, email, password });

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

        console.log("Response status:", response.status);

        const responseText = await response.text();
        console.log("Raw response:", responseText);

        let responseData;
        try {
            responseData = JSON.parse(responseText);
        } catch (parseError) {
            console.error("JSON parse error:", parseError);
            showMessage('Ошибка сервера: неверный формат ответа', 'error');
            return;
        }

        if (response.ok) {
            console.log("✅ Registration successful:", responseData);
            showMessage('Регистрация успешна! Выполняется вход...', 'success');

            // Очищаем форму
            e.target.reset();

            // Автоматически входим после регистрации
            await autoLoginAfterRegistration(email, password);

        } else {
            console.error("❌ Registration failed:", responseData);
            showMessage(responseData.detail || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        console.error('❌ Register connection error:', error);
        showMessage('Ошибка соединения с сервером. Проверьте, запущен ли сервер.', 'error');
    }
}

// Автоматический вход после регистрации
async function autoLoginAfterRegistration(email, password) {
    console.log("🔄 Auto-login after registration...");

    try {
        const loginResponse = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        console.log("Auto-login response status:", loginResponse.status);

        if (loginResponse.ok) {
            const loginData = await loginResponse.json();

            // Сохраняем токен в localStorage
            localStorage.setItem('token', loginData.access_token);
            console.log("✅ Token saved to localStorage:", loginData.access_token);

            // Обновляем глобальные переменные
            token = loginData.access_token;

            // Загружаем информацию о пользователе
            await loadCurrentUserAfterAuth();

            showMessage('Вход выполнен! Перенаправляем...', 'success');

            // Перенаправляем в кабинет
            setTimeout(() => {
                console.log("🎯 Redirecting to dashboard...");
                window.location.href = 'dashboard.html';
            }, 1000);

        } else {
            const errorData = await loginResponse.json();
            console.error("❌ Auto-login failed:", errorData);
            showMessage('Регистрация успешна, но вход не удался. Войдите manually.', 'error');

            // Перенаправляем на страницу входа
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        }
    } catch (loginError) {
        console.error("❌ Auto-login error:", loginError);
        showMessage('Ошибка автоматического входа. Войдите manually.', 'error');

        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    }
}

// Функция для загрузки пользователя после аутентификации
async function loadCurrentUserAfterAuth() {
    console.log("🔄 Loading user after auth...");

    if (!token) {
        console.log("❌ No token for loading user");
        return null;
    }

    try {
        const response = await fetch(`${API_BASE}/api/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        console.log("User load response status:", response.status);

        if (response.ok) {
            currentUser = await response.json();
            console.log("✅ User loaded after auth:", currentUser);
            return currentUser;
        } else {
            console.log("❌ Failed to load user after auth");
            return null;
        }
    } catch (error) {
        console.error('❌ Load user after auth error:', error);
        return null;
    }
}