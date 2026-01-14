"""
Тестовый скрипт для проверки работы парсинга и суммаризации
БЕЗ запуска Telegram бота
"""
import sys
from parser import extract_text_from_url, validate_url, get_text_stats
from summarizer import summarize_text, get_summary_stats

def test_url(url):
    """Тестирование на конкретном URL"""
    print(f"\n{'='*60}")
    print(f"Тестирование URL: {url}")
    print(f"{'='*60}\n")
    
    # Шаг 1: Валидация
    print("1️⃣ Валидация URL...")
    if not validate_url(url):
        print("   ❌ URL невалиден!")
        return
    print("   ✅ URL валиден")
    
    # Шаг 2: Парсинг
    print("\n2️⃣ Парсинг страницы...")
    text = extract_text_from_url(url)
    
    if not text:
        print("   ❌ Не удалось извлечь текст")
        return
    
    stats = get_text_stats(text)
    print(f"   ✅ Текст извлечен:")
    print(f"      - Символов: {stats['characters']}")
    print(f"      - Слов: {stats['words']}")
    print(f"      - Предложений: {stats['sentences']}")
    
    # Показать превью текста
    preview = text[:300] + "..." if len(text) > 300 else text
    print(f"\n   📄 Превью текста:")
    print(f"   {preview}")
    
    # Шаг 3: Суммаризация
    print("\n3️⃣ Создание краткого содержания...")
    summary = summarize_text(text)
    
    if not summary:
        print("   ❌ Не удалось создать саммари")
        return
    
    print(f"   ✅ Саммари создан!")
    print(f"\n   📝 Краткое содержание:")
    print(f"   {summary}")
    
    # Статистика
    summary_stats = get_summary_stats(text, summary)
    print(f"\n4️⃣ Статистика:")
    print(f"   - Оригинал: {summary_stats['original_words']} слов")
    print(f"   - Саммари: {summary_stats['summary_words']} слов")
    print(f"   - Степень сжатия: {summary_stats['compression_ratio']}%")
    
    print(f"\n{'='*60}")
    print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    print("\n🧪 ТЕСТОВЫЙ ЗАПУСК КОМПОНЕНТОВ БОТА")
    print("="*60)
    
    # Тестовые URL
    test_urls = [
        "https://simple.wikipedia.org/wiki/Cat",
        "https://en.wikipedia.org/wiki/Python_(programming_language)"
    ]
    
    # Если передан URL в командной строке
    if len(sys.argv) > 1:
        test_url(sys.argv[1])
    else:
        # Тестируем первый URL
        print("\nИспользуется тестовый URL (можете передать свой как аргумент)")
        print("Пример: python test_bot.py https://example.com/article")
        test_url(test_urls[0])
