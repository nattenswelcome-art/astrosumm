"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Hugging Face Token (опционально)
HF_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

# DeepSeek API Key (для улучшенной суммаризации)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Настройки обработки текста
MAX_TEXT_LENGTH = 10000  # Максимальная длина текста для обработки
SUMMARY_SENTENCES = 5     # Количество предложений в саммари по умолчанию

# Настройки парсинга
REQUEST_TIMEOUT = 30  # Таймаут для HTTP запросов (секунды)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Проверка наличия обязательных переменных
if not TELEGRAM_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN не найден! "
        "Создайте .env файл на основе .env.example и укажите токен бота."
    )
