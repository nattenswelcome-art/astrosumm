# 🐛 Bug Report - Telegram Summarizer Bot

**Дата проверки:** 2026-01-18  
**Проверено:** Roo AI (Debug Mode)  
**Статус:** 🔴 КРИТИЧЕСКИЕ БАГИ ОБНАРУЖЕНЫ

---

## 📋 Краткое резюме

Обнаружено **2 критических бага** и **2 проблемы конфигурации**, которые требуют немедленного исправления для корректной работы бота.

---

## 🔴 КРИТИЧЕСКИЕ БАГИ

### 1. ❌ Отсутствует зависимость numpy в requirements.txt

**Файл:** [`requirements.txt`](requirements.txt:1)  
**Серьезность:** 🔴 КРИТИЧЕСКАЯ  
**Статус:** Не исправлено

**Описание:**
Библиотека `numpy` отсутствует в файле зависимостей, но является обязательной для работы модуля суммаризации Sumy.

**Ошибка:**
```
LSA summarizer requires NumPy. Please, install it by command 'pip install numpy'.
```

**Воспроизведение:**
```bash
python3 -c "from summarizer import summarize_text; print(summarize_text('test text'))"
# Output: None (summarization fails)
```

**Влияние:**
- ✅ DeepSeek API не работает (нет баланса) → fallback к HF API
- ✅ HuggingFace API не работает (404) → fallback к extractive методу  
- ❌ Extractive метод падает из-за отсутствия numpy
- **Результат:** Бот полностью не может создавать саммари!

**Исправление:**
```diff
# requirements.txt
python-telegram-bot>=21.0
beautifulsoup4==4.12.3
requests==2.31.0
trafilatura>=1.8.0
python-dotenv==1.0.0
sumy==0.11.0
nltk==3.8.1
lxml>=5.0.0
deep-translator==1.11.4
flask==3.0.0
+numpy>=1.24.0
```

**Временное решение:**
```bash
pip3 install numpy
```

---

### 2. ❌ Логическая ошибка в js_parser.py

**Файл:** [`js_parser.py`](js_parser.py:82)  
**Строка:** 82  
**Серьезность:** 🔴 КРИТИЧЕСКАЯ  
**Статус:** Не исправлено

**Описание:**
Попытка получить текст из страницы (`page.text_content('body')`) происходит ПОСЛЕ закрытия браузера (`await browser.close()`).

**Код с ошибкой:**
```python
# Строка 65-66
await browser.close()

# Использовать trafilatura для извлечения чистого текста
text = trafilatura.extract(...)

if text:
    return text
else:
    # Строка 80-84 - ОШИБКА!
    logger.warning("Trafilatura не смог извлечь, используем page.text_content()")
    text_content = await page.text_content('body')  # ❌ page уже не существует!
    if text_content:
        return text_content
```

**Влияние:**
- JS-сайты (Medium, Dzen.ru, Twitter и др.) не будут корректно парситься
- Fallback механизм для JS-сайтов не работает
- Пользователи получат ошибку для динамических сайтов

**Исправление:**
```python
# Получение HTML контента после выполнения JS
content = await page.content()

# СНАЧАЛА попробуем text_content как fallback
text_content_backup = None
try:
    text_content_backup = await page.text_content('body')
except:
    pass

logger.info(f"HTML получен: {len(content)} символов")

# ЗАТЕМ закрыть браузер
await browser.close()

# Использовать trafilatura для извлечения чистого текста
text = trafilatura.extract(
    content,
    include_comments=False,
    include_tables=False,
    no_fallback=False
)

if text:
    logger.info(f"Текст успешно извлечен через Playwright: {len(text)} символов")
    return text
elif text_content_backup:
    # Используем резервный текст
    logger.warning("Trafilatura не смог извлечь, используем page.text_content()")
    return text_content_backup
else:
    logger.error("Не удалось извлечь текст даже после рендеринга JS")
    return None
```

---

## ⚠️ ПРОБЛЕМЫ КОНФИГУРАЦИИ

### 3. ⚠️ DeepSeek API - недостаточно баланса

**Файл:** [`.env`](.env:5)  
**Серьезность:** ⚠️ СРЕДНЯЯ  
**Статус:** Требует внимания

**Ошибка:**
```json
{
  "error": {
    "message": "Insufficient Balance",
    "type": "unknown_error",
    "code": "invalid_request_error"
  }
}
```

**Статус код:** 402 Payment Required

**Влияние:**
- DeepSeek API не работает → автоматический fallback к extractive методу
- Качество суммаризации ниже (extractive vs AI-powered)
- Бот работает, но с худшим качеством

**Рекомендации:**
1. Пополнить баланс DeepSeek API (очень дешево: ~$0.14 за 1M токенов)
2. Или удалить ключ из `.env` если не планируете использовать
3. Или использовать другой AI API (Claude, GPT, Groq)

---

### 4. ⚠️ HuggingFace API - модель недоступна

**Файл:** [`summarizer.py`](summarizer.py:95)  
**Серьезность:** ⚠️ НИЗКАЯ  
**Статус:** Известная проблема

**Ошибка:**
```
HF API вернул статус 404: Not Found
```

**Причина:**
Модель `facebook/bart-large-cnn` на HuggingFace Router недоступна или эндпоинт изменился.

**Влияние:**
- HF API fallback не работает
- Бот использует extractive метод (работает после установки numpy)

**Рекомендации:**
- Использовать DeepSeek вместо HF (лучше качество, дешевле)
- Или обновить эндпоинт HF API

---

## ⚡ ПРЕДУПРЕЖДЕНИЯ

### 5. ⚡ Конфликт множественных инстансов бота

**Источник:** [`bot.log`](bot.log:1)  
**Серьезность:** ⚡ ИНФОРМАЦИОННАЯ  

**Лог:**
```
ERROR - Ошибка при обработке обновления: Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

**Причина:**
Запущено несколько экземпляров бота одновременно (локально и/или на сервере).

**Влияние:**
- Боты конфликтуют друг с другом
- Сообщения обрабатываются непредсказуемо

**Решение:**
```bash
# Остановить все запущенные инстансы
pkill -f "python.*main.py"

# Запустить только один
python3 main.py
```

---

## 📊 Итоговая таблица багов

| # | Баг | Файл | Строка | Серьезность | Статус |
|---|-----|------|--------|-------------|--------|
| 1 | Отсутствует numpy | requirements.txt | - | 🔴 Критический | ❌ Не исправлено |
| 2 | Логическая ошибка в JS парсере | js_parser.py | 82 | 🔴 Критический | ❌ Не исправлено |
| 3 | DeepSeek нет баланса | .env | 5 | ⚠️ Средний | ⚠️ Конфигурация |
| 4 | HF API 404 | summarizer.py | 95 | ⚠️ Низкий | ⚠️ Известная проблема |
| 5 | Множественные инстансы | - | - | ⚡ Info | ⚡ Предупреждение |

---

## ✅ Что работает корректно

- ✅ Конфигурация загружается правильно
- ✅ Telegram Bot API подключение работает
- ✅ Парсинг обычных сайтов работает (trafilatura)
- ✅ Перевод на русский работает отлично (Google Translate)
- ✅ Модуль валидации URL работает
- ✅ Обработчики команд настроены правильно
- ✅ Error handler установлен
- ✅ Inline кнопки работают
- ✅ Кэширование переводов работает

---

## 🔧 План исправления (Priority Order)

### Шаг 1: Исправить критические баги
```bash
# 1. Добавить numpy в requirements.txt
echo "numpy>=1.24.0" >> requirements.txt
pip3 install numpy

# 2. Исправить js_parser.py (см. патч выше)
```

### Шаг 2: Проверить работу
```bash
# Протестировать суммаризацию
python3 -c "
from summarizer import summarize_text
text = 'This is a test. ' * 50
summary = summarize_text(text)
print(f'Works: {summary is not None}')
"
```

### Шаг 3: Решить конфигурационные проблемы
```bash
# Либо пополнить DeepSeek баланс
# Либо удалить ключ:
# sed -i '' 's/^DEEPSEEK_API_KEY=/#DEEPSEEK_API_KEY=/' .env
```

### Шаг 4: Перезапустить бота
```bash
# Остановить все инстансы
pkill -f "python.*main.py"

# Запустить чистую версию
python3 main.py
```

---

## 🧪 Команды для тестирования

```bash
# Тест парсинга
python3 test_bot.py https://simple.wikipedia.org/wiki/Cat

# Тест инициализации
python3 test_init.py

# Тест перевода
python3 test_translator.py

# Запуск бота
python3 main.py
```

---

## 📝 Рекомендации

### Немедленные действия:
1. ✅ Добавить `numpy>=1.24.0` в requirements.txt
2. ✅ Исправить логическую ошибку в js_parser.py:82
3. ✅ Остановить дублирующиеся инстансы бота

### Долгосрочные улучшения:
1. Пополнить DeepSeek API баланс для лучшего качества
2. Добавить unit-тесты для предотвращения регрессий
3. Добавить CI/CD pipeline для автоматической проверки
4. Рассмотреть использование Playwright как опциональной зависимости

---

**Составил:** Roo AI (Debug Mode)  
**Дата:** 2026-01-18  
**Версия:** 1.0
