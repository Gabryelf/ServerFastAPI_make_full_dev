class UIService {
    static showElement(id) {
        document.getElementById(id).classList.remove('hidden');
    }

    static hideElement(id) {
        document.getElementById(id).classList.add('hidden');
    }

    static setText(id, text) {
        document.getElementById(id).textContent = text;
    }

    static showError(elementId, message) {
        this.setText(elementId, message);
        setTimeout(() => this.setText(elementId, ''), 5000);
    }

    static showSuccess(elementId, message) {
        this.setText(elementId, message);
        setTimeout(() => this.setText(elementId, ''), 3000);
    }

    static setLoading(loading = true) {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = loading;
        });
        document.body.classList.toggle('loading', loading);
    }

    static updateUserInfo(username, role) {
        this.setText('username', username);
        const roleBadge = document.getElementById('userRole');
        this.setText('userRole', role);
        roleBadge.className = `role-badge ${role}`;
    }

    static showUserInterface(user) {
        this.hideElement('authSection');
        this.showElement('userInfo');
        this.showElement('ordersSection');
        this.updateUserInfo(user.username, user.role);

        if (user.role === 'seller' || user.role === 'admin') {
            this.showElement('productForm');
        }
    }

    static showAuthInterface() {
        this.showElement('authSection');
        this.hideElement('userInfo');
        this.hideElement('productForm');
        this.hideElement('ordersSection');
    }

    static clearForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
    }
}