# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скачиваем NLTK данные
RUN python -c "import nltk; nltk.download('punkt')"

# Копируем все файлы проекта
COPY . .

# Команда запуска
CMD ["python", "main.py"]
