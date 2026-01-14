"""
Модуль для парсинга веб-контента
С автоматическим fallback к Playwright для JS-сайтов
"""
import trafilatura
import requests
from typing import Optional
import config
import logging

logger = logging.getLogger(__name__)

# Попытка импортировать JS парсер
try:
    from js_parser import extract_text_from_js_site, check_if_js_site
    HAS_PLAYWRIGHT = True
    logger.info("Playwright доступен - JS-сайты поддерживаются")
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.warning("Playwright не установлен - JS-сайты не поддерживаются")


def validate_url(url: str) -> bool:
    """
    Проверяет валидность URL
    
    Args:
        url: URL для проверки
        
    Returns:
        True если URL валиден, иначе False
    """
    if not url:
        return False
    
    # Проверка что URL начинается с http:// или https://
    return url.startswith(('http://', 'https://'))


async def extract_text_from_url(url: str) -> Optional[str]:
    """
    Извлекает текстовый контент из веб-страницы
    С автоматическим fallback к Playwright для JS-сайтов
    
    Args:
        url: URL страницы для парсинга
        
    Returns:
        Извлеченный текст или None в случае ошибки
    """
    try:
        logger.info(f"Начало парсинга URL: {url}")
        
        # Попытка 1: Обычный парсинг через trafilatura (быстрее)
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded:
            # Извлечение текстового контента
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
                include_formatting=False,
                include_links=False,
                include_images=False
            )
            
            # Если получили достаточно текста - используем
            if text and len(text) > 100:
                # Ограничение длины текста
                if len(text) > config.MAX_TEXT_LENGTH:
                    logger.info(f"Текст обрезан с {len(text)} до {config.MAX_TEXT_LENGTH} символов")
                    text = text[:config.MAX_TEXT_LENGTH]
                
                logger.info(f"Успешно извлечено {len(text)} символов через trafilatura")
                return text
        
        # Попытка 2: JS парсер через Playwright (если доступен)
        if HAS_PLAYWRIGHT:
            logger.info(f"Trafilatura не сработал, пробуем Playwright для JS-контента...")
            
            # Используем Playwright
            text = await extract_text_from_js_site(url)
            
            if text:
                # Ограничение длины
                if len(text) > config.MAX_TEXT_LENGTH:
                    logger.info(f"JS текст обрезан с {len(text)} до {config.MAX_TEXT_LENGTH}")
                    text = text[:config.MAX_TEXT_LENGTH]
                
                logger.info(f"Успешно извлечено {len(text)} символов через Playwright")
                return text
        
        # Если ничего не сработало
        logger.error(f"Не удалось извлечь текст из {url}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Таймаут при загрузке {url}")
        # Попробуем Playwright если доступен
        if HAS_PLAYWRIGHT:
            try:
                logger.info("Повтор через Playwright после таймаута...")
                text = await extract_text_from_js_site(url)
                if text:
                    return text[:config.MAX_TEXT_LENGTH]
            except:
                pass
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при парсинге {url}: {e}")
        return None


def get_text_stats(text: str) -> dict:
    """
    Возвращает статистику о тексте
    
    Args:
        text: Текст для анализа
        
    Returns:
        Словарь со статистикой
    """
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    return {
        'characters': len(text),
        'words': len(words),
        'sentences': sentences
    }
