"""
Модуль для создания кратких содержаний текста
Использует extractive метод (sumy) с опциональной поддержкой HuggingFace API
"""
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
import requests
from typing import Optional
import config
import logging

logger = logging.getLogger(__name__)


def summarize_with_hf(text: str) -> Optional[str]:
    """
    Создает краткое содержание используя Hugging Face API (бесплатно)
    
    Args:
        text: Текст для суммаризации
        
    Returns:
        Краткое содержание или None в случае ошибки
    """
    if not config.HF_TOKEN:
        logger.debug("HF_TOKEN не установлен, пропускаем HF API")
        return None
    
    HF_API_URL = "https://router.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {config.HF_TOKEN}"}
    
    try:
        # HF API принимает до 1024 токенов (~3000 символов)
        text_truncated = text[:3000]
        
        payload = {
            "inputs": text_truncated,
            "parameters": {
                "max_length": 150,
                "min_length": 40,
                "do_sample": False
            }
        }
        
        logger.info("Отправка запроса в Hugging Face API...")
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get('summary_text', '')
                logger.info(f"Получен саммари из HF API: {len(summary)} символов")
                return summary
        else:
            logger.warning(f"HF API вернул статус {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Таймаут при обращении к HF API")
        return None
    except Exception as e:
        logger.error(f"Ошибка HF API: {e}")
        return None


def summarize_extractive(text: str, sentences_count: int = None) -> Optional[str]:
    """
    Создает краткое содержание используя extractive метод (LSA алгоритм)
    Бесплатный метод, работает локально без внешних API
    
    Args:
        text: Текст для суммаризации
        sentences_count: Количество предложений в саммари
        
    Returns:
        Краткое содержание или None в случае ошибки
    """
    if sentences_count is None:
        sentences_count = config.SUMMARY_SENTENCES
    
    try:
        logger.info(f"Создание extractive саммари ({sentences_count} предложений)...")
        
        # Ограничение длины текста
        text_limited = text[:config.MAX_TEXT_LENGTH]
        
        # Парсинг текста
        parser = PlaintextParser.from_string(text_limited, Tokenizer("english"))
        
        # Создание суммаризатора (LSA - Latent Semantic Analysis)
        summarizer = LsaSummarizer()
        
        # Генерация саммари
        summary_sentences = summarizer(parser.document, sentences_count)
        
        # Преобразование в строку
        result = ' '.join([str(sentence) for sentence in summary_sentences])
        
        if not result:
            logger.error("Extractive метод вернул пустой результат")
            return None
        
        logger.info(f"Создан extractive саммари: {len(result)} символов")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка в extractive суммаризации: {e}")
        return None


def summarize_text(text: str, sentences_count: int = None) -> Optional[str]:
    """
    Главная функция для создания краткого содержания
    Пытается использовать HF API, затем fallback к extractive методу
    
    Args:
        text: Текст для суммаризации
        sentences_count: Количество предложений (для extractive метода)
        
    Returns:
        Краткое содержание или None в случае ошибки
    """
    if not text:
        return None
    
    # Проверка минимальной длины
    if len(text) < 100:
        logger.warning("Текст слишком короткий для суммаризации")
        return None
    
    # Попытка 1: Hugging Face API (если токен доступен)
    if config.HF_TOKEN:
        logger.info("Попытка использовать HF API...")
        summary = summarize_with_hf(text)
        if summary:
            return summary
        logger.info("HF API не удалось, переход к extractive методу...")
    
    # Попытка 2: Extractive метод (всегда работает)
    logger.info("Использование extractive метода...")
    summary = summarize_extractive(text, sentences_count)
    
    return summary


def get_summary_stats(original_text: str, summary_text: str) -> dict:
    """
    Возвращает статистику о созданном саммари
    
    Args:
        original_text: Оригинальный текст
        summary_text: Краткое содержание
        
    Returns:
        Словарь со статистикой
    """
    original_words = len(original_text.split())
    summary_words = len(summary_text.split())
    
    compression_ratio = 0
    if original_words > 0:
        compression_ratio = round((summary_words / original_words) * 100, 1)
    
    return {
        'original_words': original_words,
        'original_chars': len(original_text),
        'summary_words': summary_words,
        'summary_chars': len(summary_text),
        'compression_ratio': compression_ratio
    }
