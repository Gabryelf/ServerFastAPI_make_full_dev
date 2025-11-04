FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости сначала для кэширования
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем симлинк для статических файлов
RUN ln -sf /app/frontend /app/backend/static

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "backend/main.py"]