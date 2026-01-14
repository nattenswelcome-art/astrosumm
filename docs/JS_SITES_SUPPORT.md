# Поддержка JavaScript-сайтов

## 🎯 Проблема

Некоторые современные сайты (React, Vue, Angular) загружают контент через JavaScript. Текущая версия бота использует `trafilatura` который работает только со статическим HTML.

**Примеры таких сайтов:**
- https://www.astrologyzone.com (требует JS)
- https://dzen.ru (требует авторизацию + JS)
- Многие SPA (Single Page Applications)

## ✅ Решение: Playwright

### Почему Playwright?
- ✅ Рендерит JavaScript
- ✅ Бесплатный и open-source
- ✅ Поддерживает headless режим
- ✅ Быстрее Selenium
- ⚠️ Требует больше ресурсов (RAM)

---

## 📦 Установка Playwright

### Шаг 1: Добавить в requirements.txt

```python
# Добавьте эту строку в requirements.txt
playwright==1.40.0
```

### Шаг 2: Установить зависимости

```bash
cd telegram-summarizer-bot
source venv/bin/activate
pip install playwright
playwright install chromium  # Скачает браузер (~100MB)
```

---

## 💻 Реализация

### Создать новый файл `js_parser.py`:

```python
"""
Парсер для JavaScript-сайтов с использованием Playwright
"""
from playwright.async_api import async_playwright
from typing import Optional
import trafilatura
import logging

logger = logging.getLogger(__name__)


async def extract_text_from_js_site(url: str, timeout: int = 30000) -> Optional[str]:
    """
    Извлекает текст с сайтов использующих JavaScript
    
    Args:
        url: URL страницы
        timeout: Таймаут загрузки (мс)
        
    Returns:
        Извлеченный текст или None
    """
    try:
        logger.info(f"Запуск браузера для JS-сайта: {url}")
        
        async with async_playwright() as p:
            # Запуск headless браузера
            browser = await p.chromium.launch(headless=True)
            
            # Создание новой страницы
            page = await browser.new_page()
            
            # Переход на URL
            await page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Подождать дополнительную секунду для JS
            await page.wait_for_timeout(1000)
            
            # Получить HTML контент
            content = await page.content()
            
            # Закрыть браузер
            await browser.close()
            
            logger.info(f"HTML получен через Playwright: {len(content)} символов")
            
            # Использовать trafilatura для извлечения текста
            text = trafilatura.extract(content)
            
            if text:
                logger.info(f"Текст извлечен: {len(text)} символов")
                return text
            else:
                logger.warning("Trafilatura не смог извлечь текст из JS-контента")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка при парсинге JS-сайта: {e}")
        return None
```

---

## 🔄 Обновить parser.py

Добавить автоматический fallback к Playwright:

```python
import trafilatura
import requests
from typing import Optional
import config
import logging

logger = logging.getLogger(__name__)

# Импорт JS парсера (опционально)
try:
    from js_parser import extract_text_from_js_site
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.warning("Playwright не установлен - JS-сайты не поддерживаются")


async def extract_text_from_url(url: str, use_js: bool = False) -> Optional[str]:
    """
    Извлекает текст из URL
    Автоматический fallback к Playwright если trafilatura не работает
    
    Args:
        url: URL для парсинга
        use_js: Принудительно использовать JS парсер
    """
    try:
        logger.info(f"Начало парсинга URL: {url}")
        
        # Попытка 1: Обычный парсинг (быстрее)
        if not use_js:
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded:
                text = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=False,
                    no_fallback=False
                )
                
                if text and len(text) > 100:
                    logger.info(f"Текст извлечен через trafilatura: {len(text)} символов")
                    return text[:config.MAX_TEXT_LENGTH]
        
        # Попытка 2: JS парсер (если доступен)
        if HAS_PLAYWRIGHT:
            logger.info("Trafilatura не сработал, пробуем Playwright...")
            text = await extract_text_from_js_site(url)
            
            if text:
                return text[:config.MAX_TEXT_LENGTH]
        
        logger.error(f"Не удалось извлечь текст из {url}")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")
        return None
```

---

## 🔧 Обновить main.py

Сделать handle_url асинхронным для поддержки Playwright:

```python
# В main.py handle_url уже async, просто используйте await
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ...
    text = await extract_text_from_url(url)  # Добавить await
    # ...
```

---

## ⚠️ Важные замечания

### Преимущества Playwright:
- ✅ Работает с JS-сайтами
- ✅ Рендерит SPA приложения
- ✅ Может обходить простые защиты

### Недостатки:
- ⚠️ Медленнее (5-10 секунд вместо 1-2)
- ⚠️ Требует больше RAM (~300-500MB)
- ⚠️ Браузер занимает ~100MB диска
- ⚠️ Может не работать на некоторых хостингах (Render free tier)

### Рекомендации:

1. **Для MVP:** Оставить без Playwright
   - 70-80% сайтов работают
   - Меньше ресурсов
   - Быстрее работа

2. **Для Production:** Добавить Playwright как опцию
   - Использовать только для проблемных сайтов
   - Добавить команду `/parse_js <url>` для принудительного JS парсинга

---

## 🚀 Альтернативные решения

### Вариант 1: requests-html (проще Playwright)

```bash
pip install requests-html
```

```python
from requests_html import HTMLSession

session = HTMLSession()
response = session.get(url)
response.html.render()  # Рендерит JS
text = response.html.text
```

**Легче чем Playwright, но менее надежно.**

### Вариант 2: Selenium (классика)

```bash
pip install selenium
```

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(url)
html = driver.page_source
driver.quit()
```

**Работает, но медленнее Playwright.**

---

## 📊 Сравнение решений

| Инструмент | Скорость | Надежность | Легкость | RAM | Размер |
|-----------|----------|------------|----------|-----|---------|
| **trafilatura** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~50MB | ~5MB |
| **Playwright** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ~400MB | ~100MB |
| **requests-html** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~200MB | ~50MB |
| **Selenium** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ~500MB | ~150MB |

---

## 💡 Рекомендация для вашего бота

**Для текущего MVP:**
- Оставьте без JS парсинга
- 70-80% сайтов работают отлично
- Быстро и легко

**В будущем (v2.0):**
- Добавьте Playwright как опцию
- Сделайте команду `/js https://url` для принудительного JS
- Кэшируйте результаты

**Почему не сейчас:**
1. Playwright не работает на бесплатном Render.com (нужен Paid план)
2. Медленная работа на слабых серверах
3. MVP должен быть простым

---

## 🎯 Итог

**Текущий бот работает с:**
- ✅ Статическими HTML сайтами (Wikipedia, большинство новостных)
- ✅ ~70-80% веб-сайтов

**Не работает с:**
- ❌ SPA приложениями (React/Vue/Angular)
- ❌ Сайтами с авторизацией (dzen.ru)
- ❌ Защищенным контентом

**Это нормально для MVP!** 🚀

Если хотите добавить Playwright - я могу помочь, но это усложнит проект и сделает его тяжелее.
