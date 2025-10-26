// Функции для работы с кабинетом
async function loadMyItems() {
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE}/users/me/items`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const items = await response.json();
            displayItems(items, 'my-items');
        }
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

async function createItem(event) {
    event.preventDefault();

    if (!token) return;

    const formData = new FormData();
    formData.append('title', document.getElementById('item-title').value);
    formData.append('description', document.getElementById('item-description').value);

    const imageFile = document.getElementById('item-image').files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }

    try {
        const response = await fetch(`${API_BASE}/users/items`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (response.ok) {
            alert('Товар создан!');
            document.getElementById('create-item-form').style.display = 'none';
            loadMyItems();
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        alert('Ошибка соединения');
    }
}

function showCreateItemForm() {
    document.getElementById('create-item-form').style.display = 'block';
}

function displayItems(items, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = items.map(item => `
        <div class="item-card">
            <h3>${item.title}</h3>
            <p>${item.description || 'Нет описания'}</p>
            ${item.image_data ? `<img src="${API_BASE}/users/items/${item.id}/image" alt="${item.title}" style="max-width: 100%; margin-top: 1rem;">` : ''}
        </div>
    `).join('');
}