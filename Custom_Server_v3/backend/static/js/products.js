class ProductsService {
    static async loadProducts() {
        try {
            const response = await fetch('/products');
            const products = await response.json();
            this.renderProducts(products);
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    static renderProducts(products) {
        const productsList = document.getElementById('productsList');
        productsList.innerHTML = '';

        if (products.length === 0) {
            productsList.innerHTML = '<p>Товаров пока нет</p>';
            return;
        }

        products.forEach(product => {
            const productDiv = document.createElement('div');
            productDiv.className = 'product';
            productDiv.innerHTML = `
                <h3>${this.escapeHtml(product.name)}</h3>
                <p>${this.escapeHtml(product.description)}</p>
                <p><strong>Цена: ${product.price} руб.</strong></p>
                ${AuthService.isAuthenticated() ?
                    `<button onclick="ProductsService.buyProduct(${product.id})">Купить</button>` :
                    '<p><em>Войдите, чтобы купить</em></p>'
                }
            `;
            productsList.appendChild(productDiv);
        });
    }

    static async buyProduct(productId) {
        if (!AuthService.isAuthenticated()) {
            alert('Сначала войдите в систему');
            return;
        }

        UIService.setLoading(true);

        try {
            const response = await fetch(`/buy/${productId}`, {
                method: 'POST',
                headers: AuthService.getAuthHeaders()
            });

            if (response.ok) {
                alert('Товар куплен успешно!');
                OrdersService.loadMyOrders();
            } else {
                const error = await response.json();
                alert('Ошибка при покупке: ' + error.detail);
            }
        } catch (error) {
            alert('Ошибка сети: ' + error.message);
        } finally {
            UIService.setLoading(false);
        }
    }

    static async addProduct() {
        const name = document.getElementById('productName').value;
        const price = parseFloat(document.getElementById('productPrice').value);
        const description = document.getElementById('productDesc').value;

        if (!name || !price) {
            UIService.showError('productMessage', 'Заполните название и цену');
            return;
        }

        UIService.setLoading(true);

        try {
            const response = await fetch(`/products?name=${encodeURIComponent(name)}&price=${price}&description=${encodeURIComponent(description)}`, {
                method: 'POST',
                headers: AuthService.getAuthHeaders()
            });

            if (response.ok) {
                UIService.showSuccess('productMessage', 'Товар добавлен!');
                document.getElementById('productName').value = '';
                document.getElementById('productPrice').value = '';
                document.getElementById('productDesc').value = '';
                this.loadProducts();
            } else {
                const error = await response.json();
                UIService.showError('productMessage', 'Ошибка: ' + error.detail);
            }
        } catch (error) {
            UIService.showError('productMessage', 'Ошибка сети: ' + error.message);
        } finally {
            UIService.setLoading(false);
        }
    }

    static escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}