class AuthService {
    static currentUser = null;

    static async login() {
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        UIService.setLoading(true);

        try {
            const response = await fetch('/my-orders', {
                headers: {
                    'Authorization': 'Basic ' + btoa(username + ':' + password)
                }
            });

            if (response.ok) {
                this.currentUser = { username, password };
                await this.fetchUserRole();
                UIService.showUserInterface(this.currentUser);
                ProductsService.loadProducts();
                OrdersService.loadMyOrders();
            } else {
                UIService.showError('loginError', 'Ошибка авторизации: неверный логин или пароль');
            }
        } catch (error) {
            UIService.showError('loginError', 'Ошибка сети: ' + error.message);
        } finally {
            UIService.setLoading(false);
        }
    }

    static async register() {
        const username = document.getElementById('regUsername').value;
        const password = document.getElementById('regPassword').value;
        const role = document.getElementById('regRole').value;

        UIService.setLoading(true);

        const userData = {
            username: username,
            password: password,
            role: role
        };

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                UIService.showSuccess('regSuccess', 'Регистрация успешна! Теперь войдите в систему.');
                UIService.clearForm('regUsername');
                UIService.clearForm('regPassword');
            } else {
                const errorData = await response.json();
                UIService.showError('regError', errorData.detail || 'Ошибка регистрации');
            }
        } catch (error) {
            UIService.showError('regError', 'Ошибка сети: ' + error.message);
        } finally {
            UIService.setLoading(false);
        }
    }

    static async fetchUserRole() {
        try {
            if (this.currentUser.username === 'admin') {
                this.currentUser.role = 'admin';
            } else if (this.currentUser.username === 'seller1' || this.currentUser.username.startsWith('seller')) {
                this.currentUser.role = 'seller';
            } else {
                this.currentUser.role = 'customer';
            }
        } catch (error) {
            console.error('Error fetching user role:', error);
        }
    }

    static logout() {
        this.currentUser = null;
        UIService.showAuthInterface();
        ProductsService.loadProducts();
    }

    static getAuthHeaders() {
        if (!this.currentUser) return {};

        return {
            'Authorization': 'Basic ' + btoa(this.currentUser.username + ':' + this.currentUser.password)
        };
    }

    static isAuthenticated() {
        return this.currentUser !== null;
    }
}