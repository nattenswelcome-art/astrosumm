"""
Модуль для парсинга JavaScript-сайтов используя Playwright
Используется как fallback когда trafilatura не работает
"""
from playwright.async_api import async_playwright
from typing import Optional
import trafilatura
import logging

logger = logging.getLogger(__name__)


async def extract_text_from_js_site(url: str, timeout: int = 30000) -> Optional[str]:
    """
    Извлекает текст с сайтов которые используют JavaScript для загрузки контента
    
    Args:
        url: URL страницы для парсинга
        timeout: Таймаут загрузки в миллисекундах (по умолчанию 30 секунд)
        
    Returns:
        Извлеченный текст или None в случае ошибки
    """
    try:
        logger.info(f"Запуск Playwright браузера для: {url}")
        
        async with async_playwright() as p:
            # Запуск headless Chromium браузера
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            # Создание новой страницы
            page = await browser.new_page()
            
            # Настройка User-Agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logger.info(f"Загрузка страницы {url}...")
            
            # Переход на URL и ожидание полной загрузки
            try:
                await page.goto(url, wait_until='networkidle', timeout=timeout)
            except Exception as e:
                logger.warning(f"Ошибка при ожидании networkidle: {e}, продолжаем...")
                # Попробуем хотя бы domcontentloaded
                await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            # Дополнительное ожидание для JavaScript
            await page.wait_for_timeout(2000)
            
            # Получение HTML контента после выполнения JS
            content = await page.content()
            
            logger.info(f"HTML получен: {len(content)} символов")
            
            # Закрыть браузер
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
            else:
                # Если trafilatura не сработал, попробуем взять весь текст страницы
                logger.warning("Trafilatura не смог извлечь, используем page.text_content()")
                text_content = await page.text_content('body')
                if text_content:
                    return text_content
                logger.error("Не удалось извлечь текст даже после рендеринга JS")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка при парсинге JS-сайта {url}: {e}")
        return None


async def check_if_js_site(url: str) -> bool:
    """
    Простая эвристика для определения нужен ли Playwright
    
    Args:
        url: URL для проверки
        
    Returns:
        True если вероятно нужен JS парсер
    """
    # Известные JS-тяжелые сайты
    js_domains = [
        'astrologyzone.com',
        'dzen.ru',
        'medium.com',  # Иногда требует JS
        'twitter.com',
        'x.com',
        'instagram.com',
        'facebook.com'
    ]
    
    for domain in js_domains:
        if domain in url.lower():
            logger.info(f"Обнаружен JS-сайт по домену: {domain}")
            return True
    
    return False
