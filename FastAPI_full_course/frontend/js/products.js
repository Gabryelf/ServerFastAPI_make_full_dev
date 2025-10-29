// Загрузка всех товаров
async function loadAllProducts() {
    const grid = document.getElementById('products-grid');
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('empty-state');
    const count = document.getElementById('products-count');

    try {
        const response = await fetch(`${API_BASE}/api/products/`);
        const products = await response.json();

        loading.style.display = 'none';

        if (products.length === 0) {
            emptyState.style.display = 'block';
            count.textContent = '0';
            return;
        }

        count.textContent = products.length;
        grid.innerHTML = '';

        products.forEach(product => {
            const firstImage = product.image_paths && product.image_paths.length > 0
                ? product.image_paths[0]
                : '/static/uploads/default-product.jpg';

            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.onclick = () => viewProductDetail(product.id);

            productCard.innerHTML = `
                <img src="${API_BASE}${firstImage}" alt="${product.name}" class="product-image"
                     onerror="this.src='${API_BASE}/static/uploads/default-product.jpg'">
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-description">${product.description}</p>
                    <p class="product-owner">Продавец: ${product.owner_name || 'Неизвестно'}</p>
                </div>
            `;

            grid.appendChild(productCard);
        });

    } catch (error) {
        console.error('Load products error:', error);
        loading.innerHTML = 'Ошибка загрузки товаров';
    }
}

// Загрузка моих товаров
async function loadMyProducts() {
    const grid = document.getElementById('my-products-grid');
    const emptyState = document.getElementById('my-products-empty');

    if (!currentUser) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/products/`);
        const allProducts = await response.json();
        const myProducts = allProducts.filter(product => product.owner_id === currentUser.id);

        if (myProducts.length === 0) {
            emptyState.style.display = 'block';
            grid.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        grid.style.display = 'grid';
        grid.innerHTML = '';

        myProducts.forEach(product => {
            const firstImage = product.image_paths && product.image_paths.length > 0
                ? product.image_paths[0]
                : '/static/uploads/default-product.jpg';

            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.onclick = () => viewProductDetail(product.id);

            productCard.innerHTML = `
                <img src="${API_BASE}${firstImage}" alt="${product.name}" class="product-image"
                     onerror="this.src='${API_BASE}/static/uploads/default-product.jpg'">
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-description">${product.description}</p>
                    <div class="product-actions">
                        <button onclick="event.stopPropagation(); deleteProduct(${product.id})"
                                class="btn btn-outline btn-small">
                            Удалить
                        </button>
                    </div>
                </div>
            `;

            grid.appendChild(productCard);
        });

    } catch (error) {
        console.error('Load my products error:', error);
    }
}

// Просмотр деталей товара
async function loadProductDetail(productId) {
    const container = document.getElementById('product-detail');

    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}`);
        const product = await response.json();

        const firstImage = product.image_paths && product.image_paths.length > 0
            ? product.image_paths[0]
            : '/static/uploads/default-product.jpg';

        let galleryHTML = '';
        if (product.image_paths && product.image_paths.length > 0) {
            galleryHTML = `
                <div class="product-gallery">
                    <div class="main-image">
                        <img src="${API_BASE}${firstImage}" alt="${product.name}"
                             onerror="this.src='${API_BASE}/static/uploads/default-product.jpg'">
                    </div>
                    ${product.image_paths.slice(1).map((image, index) => `
                        <img src="${API_BASE}${image}" alt="${product.name}" class="thumbnail"
                             onerror="this.src='${API_BASE}/static/uploads/default-product.jpg'">
                    `).join('')}
                </div>
            `;
        }

        let videosHTML = '';
        if (product.video_paths && product.video_paths.length > 0) {
            videosHTML = `
                <div class="videos-section">
                    <h3>Видео</h3>
                    <div class="videos-grid">
                        ${product.video_paths.map(video => `
                            <video controls class="product-video">
                                <source src="${API_BASE}${video}" type="video/mp4">
                                Ваш браузер не поддерживает видео.
                            </video>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        let actionsHTML = '';
        if (currentUser && (currentUser.role === 'admin' || currentUser.id === product.owner_id)) {
            actionsHTML = `
                <div class="product-actions">
                    <button onclick="deleteProduct(${product.id})" class="btn btn-danger">
                        Удалить товар
                    </button>
                </div>
            `;
        }

        container.innerHTML = `
            ${galleryHTML}
            <div class="product-info-detail">
                <h1 class="product-title">${product.name}</h1>
                <p class="product-description-detail">${product.description}</p>
                ${videosHTML}
                <div class="product-meta">
                    <span>Продавец: ${product.owner_name || 'Неизвестно'}</span>
                    ${actionsHTML}
                </div>
            </div>
        `;

    } catch (error) {
        console.error('Load product detail error:', error);
        container.innerHTML = '<p>Ошибка загрузки товара</p>';
    }
}

function viewProductDetail(productId) {
    window.location.href = `product-detail.html?id=${productId}`;
}

// Создание товара
async function createProduct(formData) {
    if (!currentUser) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/products/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            // Не устанавливаем Content-Type, браузер сам установит с boundary
            // 'Content-Type': 'multipart/form-data'
            // Заголовок Authorization должен быть установлен
            'Accept': 'application/json'
            // Убираем Content-Type чтобы браузер сам установил правильный с boundary
            // 'Content-Type': `multipart/form-data; boundary=${formData._boundary}`
        },
            body: formData,
        });

        if (response.ok) {
            const newProduct = await response.json();
            showMessage('Товар успешно создан!', 'success');
            hideModal('create-product-modal');

            // Перезагружаем страницу или обновляем список
            if (window.location.pathname.includes('dashboard.html')) {
                loadMyProducts();
            } else {
                window.location.href = 'dashboard.html';
            }
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка создания товара', 'error');
        }
    } catch (error) {
        console.error('Create product error:', error);
        showMessage('Ошибка соединения', 'error');
    }
}

// Удаление товара
async function deleteProduct(productId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) return;

    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
            // Убираем Accept так как DELETE endpoint возвращает простой JSON
            // 'Accept': 'application/json'
        },
        });

        if (response.ok) {
            showMessage('Товар успешно удален!', 'success');

            // Обновляем страницу в зависимости от текущего контекста
            if (window.location.pathname.includes('product-detail.html')) {
                window.location.href = 'products.html';
            } else {
                loadMyProducts();
                loadAllProducts();
            }
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка удаления товара', 'error');
        }
    } catch (error) {
        console.error('Delete product error:', error);
        showMessage('Ошибка соединения', 'error');
    }
}

// Функции для модальных окон
function showCreateProductModal() {
    if (!currentUser) {
        window.location.href = 'login.html';
        return;
    }
    showModal('create-product-modal');
}

// Обработчик формы создания товара
document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('create-product-form');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData();
            formData.append('name', document.getElementById('product-name').value);
            formData.append('description', document.getElementById('product-description').value);

            const imagesInput = document.getElementById('product-images');
            const videosInput = document.getElementById('product-videos');

            // Добавляем изображения
            for (let i = 0; i < imagesInput.files.length; i++) {
                formData.append('images', imagesInput.files[i]);
            }

            // Добавляем видео
            for (let i = 0; i < videosInput.files.length; i++) {
                formData.append('videos', videosInput.files[i]);
            }

            await createProduct(formData);
        });
    }

    // Загрузка товаров на соответствующих страницах
    if (window.location.pathname.includes('products.html')) {
        loadAllProducts();
    }

    if (window.location.pathname.includes('dashboard.html')) {
        loadMyProducts();
        // Обновляем приветствие
        const welcome = document.getElementById('user-welcome');
        if (welcome && currentUser) {
            welcome.textContent = `Добро пожаловать, ${currentUser.full_name}!`;
        }
    }
});