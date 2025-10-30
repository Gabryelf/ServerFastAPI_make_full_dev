class AuthManager {
    constructor() {
        this.initEvents();
    }

    initEvents() {
        // Регистрация
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Логин
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Валидация пароля при регистрации
        const confirmPassword = document.getElementById('confirmPassword');
        if (confirmPassword) {
            confirmPassword.addEventListener('input', () => this.validatePasswordMatch());
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        this.clearErrors();

        const formData = new FormData(e.target);
        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            full_name: formData.get('full_name'),
            password: formData.get('password')
        };

        console.log('Register data:', userData);

        // Валидация
        if (!this.validateRegisterForm(userData)) {
            return;
        }

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();
            console.log('Register response:', result);

            if (response.ok) {
                this.showMessage('Регистрация успешна! Теперь вы можете войти.', 'success');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                this.showError('register', result.detail);
            }
        } catch (error) {
            console.error('Register error:', error);
            this.showMessage('Ошибка сети. Попробуйте позже.', 'error');
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        this.clearErrors();

        const formData = new FormData(e.target);
        const loginData = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        console.log('Login data:', loginData);

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginData)
            });

            const result = await response.json();
            console.log('Login response:', result);

            if (response.ok) {
                this.showMessage('Вход успешен!', 'success');
                // Сохраняем данные пользователя
                localStorage.setItem('user', JSON.stringify(result));
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                this.showError('login', result.detail);
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('Ошибка сети. Попробуйте позже.', 'error');
        }
    }

    validateRegisterForm(userData) {
        let isValid = true;

        // Проверка имени пользователя
        if (userData.username.length < 3) {
            this.showFieldError('username', 'Имя пользователя должно быть не менее 3 символов');
            isValid = false;
        }

        // Проверка email
        if (!this.isValidEmail(userData.email)) {
            this.showFieldError('email', 'Введите корректный email');
            isValid = false;
        }

        // Проверка пароля
        if (userData.password.length < 6) {
            this.showFieldError('password', 'Пароль должен быть не менее 6 символов');
            isValid = false;
        }

        // Проверка совпадения паролей
        if (!this.validatePasswordMatch()) {
            isValid = false;
        }

        return isValid;
    }

    validatePasswordMatch() {
        const password = document.getElementById('password')?.value;
        const confirmPassword = document.getElementById('confirmPassword')?.value;
        const errorElement = document.getElementById('confirmPasswordError');

        if (password && confirmPassword && password !== confirmPassword) {
            if (errorElement) {
                errorElement.textContent = 'Пароли не совпадают';
            }
            return false;
        } else if (errorElement) {
            errorElement.textContent = '';
        }
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showFieldError(fieldName, message) {
        const errorElement = document.getElementById(fieldName + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    showError(formType, message) {
        // Показываем общую ошибку
        this.showMessage(message, 'error');
    }

    clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(element => {
            element.textContent = '';
        });
    }

    showMessage(message, type) {
        // Создаем элемент сообщения
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.textContent = message;

        // Стили для сообщения
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            max-width: 300px;
            ${type === 'success' ? 'background: #27ae60;' : 'background: #e74c3c;'}
        `;

        document.body.appendChild(messageDiv);

        // Удаляем сообщение через 5 секунд
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new AuthManager();
});