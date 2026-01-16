# 🚀 Инструкция по деплою бота на Render

## ✅ Что уже готово:
1. Код обновлен с улучшениями:
   - DeepSeek API для лучшей суммаризации
   - Прогресс-бар остается видимым
   - Перевод в отдельном сообщении
   - Playwright для JS-сайтов

2. Код залит на GitHub: https://github.com/nattenswelcome-art/astrosumm
3. Конфигурационные файлы готовы:
   - `render.yaml` - настройки Render
   - `requirements.txt` - зависимости Python
   - `.env.example` - пример переменных окружения

## 📝 Шаги для деплоя на Render:

### Шаг 1: Регистрация на Render
1. Перейдите на https://dashboard.render.com/register
2. Зарегистрируйтесь через GitHub (это упростит подключение репозитория)
3. Подтвердите email

### Шаг 2: Создание нового сервиса
1. На главной странице Render нажмите **"New +"**
2. Выберите **"Web Service"**
3. Подключите ваш GitHub репозиторий: `nattenswelcome-art/astrosumm`
4. Если репозиторий не виден - нажмите "Configure GitHub App" и дайте доступ

### Шаг 3: Настройка сервиса
Заполните поля:

**Basic Settings:**
- **Name**: `telegram-summarizer-bot` (или любое имя)
- **Region**: `Oregon (US West)` (бесплатный план)
- **Branch**: `main`
- **Root Directory**: оставьте пустым
- **Runtime**: `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python main.py
```

### Шаг 4: Настройка переменных окружения
Нажмите **"Advanced"** и добавьте переменные окружения (Environment Variables):

1. **TELEGRAM_BOT_TOKEN**
   - Value: `7762151499:AAF5s48EtJfXC-DiJnPGmIY1mu9ghq_SYLI`

2. **DEEPSEEK_API_KEY** (если есть)
   - Value: ваш ключ DeepSeek API
   - Где взять: https://platform.deepseek.com

3. **HUGGINGFACE_TOKEN** (опционально)
   - Value: ваш токен HuggingFace
   - Где взять: https://huggingface.co/settings/tokens

### Шаг 5: Выбор плана
- Выберите **"Free"** plan
- Ограничения: 750 часов в месяц (достаточно)

### Шаг 6: Деплой
1. Нажмите **"Create Web Service"**
2. Render автоматически:
   - Склонирует репозиторий
   - Установит зависимости
   - Запустит бота
3. Процесс займет 2-3 минуты

### Шаг 7: Проверка
После деплоя:
1. Откройте бота в Telegram
2. Отправьте `/start`
3. Отправьте тестовую ссылку: `https://en.wikipedia.org/wiki/Python`
4. Проверьте все улучшения:
   - ✅ Прогресс-бар остается видимым
   - ✅ Результат в новом сообщении
   - ✅ Перевод в новом сообщении (не заменяет английскую версию)

## 🔄 Автоматическое обновление
Render автоматически обновит бота при каждом `git push` на GitHub!

## ⚠️ Важно:
1. Бесплатный план Render "засыпает" через 15 минут неактивности
2. Первый запрос после "сна" займет ~30 секунд (холодный старт)
3. Playwright НЕ будет работать на бесплатном плане (нет браузера)

## 🎯 Альтернатива для Playwright:
Если нужна поддержка JS-сайтов, используйте Heroku или VPS.

## 📞 Поддержка
Если возникнут проблемы:
- Логи: Dashboard → ваш сервис → Logs
- Документация: https://render.com/docs
