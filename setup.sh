#!/bin/bash

# Скрипт установки и запуска Telegram Summarizer Bot
# Работает на macOS и Linux

echo "🚀 Установка Telegram Summarizer Bot"
echo "======================================"
echo ""

# Проверка Python
echo "📋 Проверка Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "✅ Python найден: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "✅ Python найден: $(python --version)"
else
    echo "❌ Python не установлен!"
    echo "Установите Python с https://www.python.org/downloads/"
    exit 1
fi

# Проверка pip
echo ""
echo "📋 Проверка pip..."
if command -v pip3 &> /dev/null; then
    PIP_CMD=pip3
    echo "✅ pip найден"
elif command -v pip &> /dev/null; then
    PIP_CMD=pip
    echo "✅ pip найден"
else
    echo "❌ pip не установлен!"
    exit 1
fi

# Создание виртуального окружения
echo ""
echo "🔧 Создание виртуального окружения..."
$PYTHON_CMD -m venv venv
if [ $? -eq 0 ]; then
    echo "✅ Виртуальное окружение создано"
else
    echo "❌ Ошибка создания виртуального окружения"
    exit 1
fi

# Активация виртуального окружения
echo ""
echo "⚡ Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo ""
echo "📦 Установка зависимостей (может занять 1-2 минуты)..."
$PIP_CMD install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены"
else
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

# Скачивание NLTK данных
echo ""
echo "📚 Скачивание NLTK данных..."
$PYTHON_CMD -c "import nltk; nltk.download('punkt')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ NLTK данные скачаны"
else
    echo "❌ Ошибка скачивания NLTK данных"
    exit 1
fi

# Проверка .env файла
echo ""
echo "🔑 Проверка .env файла..."
if [ -f .env ]; then
    if grep -q "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env || grep -q "TELEGRAM_BOT_TOKEN=$" .env; then
        echo "⚠️  .env файл найден, но токен не настроен!"
        echo "Отредактируйте файл .env и укажите ваш TELEGRAM_BOT_TOKEN"
        exit 1
    else
        echo "✅ .env файл настроен"
    fi
else
    echo "⚠️  .env файл не найден!"
    echo "Создайте .env файл на основе .env.example"
    exit 1
fi

# Все готово
echo ""
echo "✅ Установка завершена успешно!"
echo ""
echo "======================================"
echo "🎉 Бот готов к запуску!"
echo "======================================"
echo ""
echo "Для запуска бота выполните:"
echo "  source venv/bin/activate"
echo "  $PYTHON_CMD main.py"
echo ""
echo "Или используйте скрипт:"
echo "  ./run.sh"
echo ""
