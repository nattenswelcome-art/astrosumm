# 🤖 Telegram Summarizer Bot

Telegram-бот для создания кратких содержаний веб-статей на английском языке.

**MVP версия на 100% бесплатных инструментах** 🎉

## ✨ Возможности

- 📄 Парсинг текстового контента с веб-сайтов
- 📝 Создание кратких содержаний (суммаризация)
- 📊 Статистика (количество слов, степень сжатия)
- 🆓 Полностью бесплатный стек технологий
- 🚀 Готов к деплою на бесплатном хостинге

## 🛠 Технологии

- **Python 3.11+**
- **python-telegram-bot** - взаимодействие с Telegram API
- **trafilatura** - парсинг веб-страниц
- **sumy** - extractive суммаризация
- **Опционально: HuggingFace API** - улучшенное качество саммари

## 📋 Требования

- Python 3.9 или выше
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- Опционально: HuggingFace Token для улучшения качества

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd telegram-summarizer-bot
```

### 2. Создание виртуального окружения

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать
# На Windows:
venv\Scripts\activate
# На Linux/macOS:
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Скачивание NLTK данных

```bash
python -c "import nltk; nltk.download('punkt')"
```

### 5. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Откройте `.env` и укажите токены:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
HUGGINGFACE_TOKEN=your_huggingface_token_here  # Опционально
```

#### Как получить токены:

**Telegram Bot Token:**
1. Открыть [@BotFather](https://t.me/botfather) в Telegram
2. Отправить `/newbot`
3. Следовать инструкциям
4. Скопировать полученный токен

**HuggingFace Token (опционально):**
1. Зарегистрироваться на [huggingface.co](https://huggingface.co)
2. Settings → Access Tokens
3. Create new token (Read type)
4. Скопировать токен

### 6. Запуск бота

```bash
python main.py
```

Бот запущен! Найдите его в Telegram и отправьте `/start`

## 📁 Структура проекта

```
telegram-summarizer-bot/
├── main.py              # Главный файл бота
├── config.py            # Конфигурация
├── parser.py            # Парсинг веб-страниц
├── summarizer.py        # Суммаризация текста
├── requirements.txt     # Зависимости Python
├── .env.example         # Пример переменных окружения
├── .gitignore          # Git ignore файл
├── Dockerfile          # Docker конфигурация
├── docker-compose.yml  # Docker Compose
├── Procfile            # Для Heroku-совместимых платформ
├── runtime.txt         # Версия Python
├── render.yaml         # Конфигурация для Render.com
└── README.md           # Этот файл
```

## 🎮 Использование

### Команды бота:

- `/start` - Начать работу с ботом
- `/help` - Справка по использованию
- `/about` - Информация о боте

### Как использовать:

1. Отправьте боту ссылку на статью
2. Дождитесь обработки (5-15 секунд)
3. Получите краткое содержание и статистику

### Пример:

```
Вы → https://en.wikipedia.org/wiki/Artificial_intelligence

Бот → ✅ Краткое содержание готово!

📝 Содержание:
Artificial intelligence (AI) is intelligence demonstrated by machines...
[краткое содержание на 3-5 предложений]

📊 Статистика:
📄 Исходный текст: 1250 слов
📝 Краткое содержание: 89 слов
🗜 Степень сжатия: 7.1%
```

## 🐳 Docker

### Запуск с Docker:

```bash
# Создать образ
docker build -t telegram-bot .

# Запустить контейнер
docker run --env-file .env telegram-bot
```

### Запуск с Docker Compose:

```bash
docker-compose up -d
```

## ☁️ Деплой

### Вариант 1: Render.com (рекомендуется)

1. Зарегистрироваться на [render.com](https://render.com)
2. New → Web Service
3. Подключить GitHub репозиторий
4. Указать переменные окружения:
   - `TELEGRAM_BOT_TOKEN`
   - `HUGGINGFACE_TOKEN` (опционально)
5. Deploy

**Бесплатный план:** 750 часов/месяц

### Вариант 2: Railway

1. Зарегистрироваться на [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Выбрать репозиторий
4. Добавить переменные окружения
5. Deploy

**Бесплатный план:** $5 кредитов/месяц (~500 часов)

### Вариант 3: PythonAnywhere

1. Зарегистрироваться на [pythonanywhere.com](https://pythonanywhere.com)
2. Bash консоль → клонировать репозиторий
3. Установить зависимости
4. Настроить Always-on task
5. Запустить `python main.py`

### Вариант 4: Локальный компьютер

Просто запустите `python main.py` и оставьте терминал открытым.

Для фонового запуска на Linux/macOS:

```bash
nohup python main.py &
```

## 🔧 Конфигурация

Настройки в [`config.py`](config.py:1):

```python
MAX_TEXT_LENGTH = 10000      # Макс длина текста
SUMMARY_SENTENCES = 5        # Количество предложений в саммари
REQUEST_TIMEOUT = 30         # Таймаут HTTP запросов
```

## 🧪 Тестирование

Тестовые URL для проверки:

```
https://en.wikipedia.org/wiki/Python_(programming_language)
https://www.bbc.com/news (любая статья)
https://medium.com/@author/article-title
```

## ⚠️ Ограничения

- Работает только с английским языком
- Максимум 10,000 символов текста
- Не поддерживает PDF файлы
- Сайты с JavaScript могут работать некорректно
- HuggingFace API: 1,000 запросов/день (бесплатный тариф)

## 🐛 Решение проблем

### Бот не отвечает

1. Проверьте что `TELEGRAM_BOT_TOKEN` указан правильно в `.env`
2. Проверьте интернет-соединение
3. Проверьте логи в `bot.log`

### Ошибка "Не удалось извлечь текст"

1. Проверьте что URL открывается в браузере
2. Убедитесь что на странице есть текстовый контент
3. Попробуйте другой URL

### Плохое качество саммари

1. Добавьте HuggingFace Token в `.env`
2. Увеличьте `SUMMARY_SENTENCES` в [`config.py`](config.py:1)
3. Попробуйте статью с более структурированным текстом

## 📊 Методы суммаризации

### Extractive метод (по умолчанию)

- **Алгоритм:** LSA (Latent Semantic Analysis)
- **Преимущества:** Быстро, бесплатно, без лимитов
- **Недостатки:** Просто выбирает предложения, не перефразирует
- **Качество:** ⭐⭐⭐

### HuggingFace API (опциональный)

- **Модель:** facebook/bart-large-cnn
- **Преимущества:** Высокое качество, перефразирование
- **Недостатки:** 1,000 запросов/день
- **Качество:** ⭐⭐⭐⭐⭐

Бот автоматически пытается использовать HF API, затем fallback к extractive методу.

## 💰 Стоимость

**Полностью бесплатно!** $0.00/месяц 🎊

- Telegram Bot API: бесплатно
- Trafilatura: бесплатно
- Sumy: бесплатно
- HuggingFace API: 1,000 запросов/день бесплатно
- Render.com хостинг: 750 часов/месяц бесплатно

## 🔮 Будущие улучшения

- [ ] Поддержка русского языка
- [ ] Поддержка PDF файлов
- [ ] Inline кнопки для настройки длины саммари
- [ ] Кэширование результатов
- [ ] База данных для истории
- [ ] Статистика использования
- [ ] Поддержка нескольких языков

## 📝 Лицензия

MIT License - свободно используйте для любых целей

## 🤝 Вклад

Приветствуются Pull Requests и Issues!

## 📞 Поддержка

- Создайте Issue в GitHub
- Проверьте логи в `bot.log`
- Изучите документацию в [`plans/`](plans/telegram-bot-analysis.md:1)

## 🙏 Благодарности

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Trafilatura](https://github.com/adbar/trafilatura)
- [Sumy](https://github.com/miso-belica/sumy)
- [HuggingFace](https://huggingface.co/)

---

**Версия:** MVP 1.0  
**Дата:** 2026-01-14  
**Статус:** Готов к использованию ✅

Создано как демонстрация возможностей бесплатных инструментов для разработки Telegram-ботов 🚀
