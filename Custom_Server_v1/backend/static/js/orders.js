class OrdersService {
    static async loadMyOrders() {
        if (!AuthService.isAuthenticated()) return;

        try {
            const response = await fetch('/my-orders', {
                headers: AuthService.getAuthHeaders()
            });

            if (response.ok) {
                const orders = await response.json();
                this.renderOrders(orders);
            }
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    static renderOrders(orders) {
        const ordersList = document.getElementById('ordersList');
        ordersList.innerHTML = '';

        if (orders.length === 0) {
            ordersList.innerHTML = '<p>У вас пока нет заказов</p>';
            return;
        }

        orders.forEach(order => {
            const orderDiv = document.createElement('div');
            orderDiv.className = 'order-item';
            orderDiv.innerHTML = `
                <p><strong>Заказ #${order.id}</strong></p>
                <p>Товар ID: ${order.product_id}</p>
                <p>Статус: <span class="status-${order.status}">${order.status}</span></p>
            `;
            ordersList.appendChild(orderDiv);
        });
    }
}