"""
Модуль для перевода текста на русский язык
Используется deep-translator (бесплатно, Google Translate API)
"""
from deep_translator import GoogleTranslator
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def translate_to_russian(text: str) -> Optional[str]:
    """
    Переводит текст на русский язык
    
    Args:
        text: Текст для перевода (на английском)
        
    Returns:
        Переведенный текст или None в случае ошибки
    """
    try:
        logger.info(f"Начало перевода текста ({len(text)} символов)...")
        
        # Google Translate имеет лимит ~5000 символов за запрос
        # Разобьем на части если нужно
        max_chunk_size = 4500
        
        if len(text) <= max_chunk_size:
            # Переводим сразу
            translator = GoogleTranslator(source='en', target='ru')
            translated = translator.translate(text)
            logger.info(f"Перевод завершен: {len(translated)} символов")
            return translated
        else:
            # Разбиваем на части
            logger.info(f"Текст слишком длинный, разбиваем на части...")
            sentences = text.split('. ')
            translated_parts = []
            current_chunk = []
            current_length = 0
            
            translator = GoogleTranslator(source='en', target='ru')
            
            for sentence in sentences:
                sentence_with_dot = sentence + '. ' if not sentence.endswith('.') else sentence + ' '
                
                if current_length + len(sentence_with_dot) > max_chunk_size:
                    # Переводим текущий chunk
                    chunk_text = ''.join(current_chunk)
                    translated_chunk = translator.translate(chunk_text)
                    translated_parts.append(translated_chunk)
                    
                    # Начинаем новый chunk
                    current_chunk = [sentence_with_dot]
                    current_length = len(sentence_with_dot)
                else:
                    current_chunk.append(sentence_with_dot)
                    current_length += len(sentence_with_dot)
            
            # Переводим остаток
            if current_chunk:
                chunk_text = ''.join(current_chunk)
                translated_chunk = translator.translate(chunk_text)
                translated_parts.append(translated_chunk)
            
            result = ' '.join(translated_parts)
            logger.info(f"Перевод по частям завершен: {len(result)} символов")
            return result
        
    except Exception as e:
        logger.error(f"Ошибка перевода: {e}")
        return None


def detect_language(text: str) -> str:
    """
    Определяет язык текста (упрощенный метод)
    
    Args:
        text: Текст для анализа
        
    Returns:
        'ru' или 'en'
    """
    # Простое определение по наличию русских букв
    russian_chars = len([c for c in text if 'а' <= c.lower() <= 'я'])
    total_alpha = len([c for c in text if c.isalpha()])
    
    if total_alpha == 0:
        return 'en'
    
    russian_ratio = russian_chars / total_alpha
    
    if russian_ratio > 0.3:
        return 'ru'
    else:
        return 'en'
