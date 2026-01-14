#!/bin/bash

# Скрипт запуска Telegram Summarizer Bot
# Работает на macOS и Linux
# Автоматически останавливает предыдущие экземпляры

echo "🚀 Запуск Telegram Summarizer Bot"
echo "===================================="
echo ""

# Остановка предыдущих экземпляров
echo "🛑 Проверка запущенных экземпляров..."
EXISTING_PIDS=$(ps aux | grep "[p]ython.*main.py" | awk '{print $2}')

if [ ! -z "$EXISTING_PIDS" ]; then
    echo "⚠️  Найдены запущенные экземпляры, останавливаю..."
    echo "$EXISTING_PIDS" | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ Предыдущие экземпляры остановлены"
else
    echo "✅ Запущенных экземпляров не найдено"
fi

echo ""

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Сначала запустите: ./setup.sh"
    exit 1
fi

# Активация виртуального окружения
echo "⚡ Активация виртуального окружения..."
source venv/bin/activate

# Определение команды Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Проверка .env файла
if [ ! -f .env ]; then
    echo "❌ .env файл не найден!"
    echo "Создайте .env файл на основе .env.example"
    exit 1
fi

# Запуск бота
echo ""
echo "🤖 Запуск бота..."
echo "Для остановки нажмите Ctrl+C"
echo ""
echo "===================================="
echo ""

$PYTHON_CMD main.py
