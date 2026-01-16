"""
Telegram бот для создания кратких содержаний веб-статей
MVP версия на бесплатных инструментах
С поддержкой перевода на русский язык
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import config
from parser import extract_text_from_url, validate_url, get_text_stats
from summarizer import summarize_text, get_summary_stats
from translator import translate_to_russian

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")
    
    welcome_message = f"""
👋 Привет, {user.first_name}!

Я бот для создания кратких содержаний статей на английском языке.

📝 **Как пользоваться:**
1️⃣ Отправь мне ссылку на статью
2️⃣ Я извлеку текст со страницы
3️⃣ Создам краткое содержание
4️⃣ Отправлю результат с статистикой

🔗 **Поддерживаемые сайты:**
• Новостные порталы (BBC, CNN, Medium)
• Блоги и статьи
• Wikipedia
• Большинство текстовых сайтов

⚡ **Быстрый старт:**
Просто отправь мне ссылку!

Пример: https://en.wikipedia.org/wiki/Artificial_intelligence

Используй /help для дополнительной информации.
    """
    
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_message = """
❓ **Справка по использованию**

**Команды:**
/start - Начать работу с ботом
/help - Показать эту справку
/about - Информация о боте

**Как использовать:**
Просто отправьте ссылку на статью (URL должен начинаться с http:// или https://)

**Что делает бот:**
• Извлекает текстовый контент со страницы
• Создает краткое содержание (5 основных предложений)
• Показывает статистику (количество слов, степень сжатия)

**Ограничения:**
⚠️ Работает только с английским языком
⚠️ Максимум 10,000 символов текста
⚠️ Не работает с PDF файлами
⚠️ Некоторые сайты с JavaScript могут работать некорректно

**Время обработки:**
⏱️ Обычно 5-15 секунд

**Примеры ссылок:**
✅ https://www.bbc.com/news/technology-12345678
✅ https://en.wikipedia.org/wiki/Python_(programming_language)
✅ https://medium.com/@author/article-title-abc123

❌ Не поддерживается: PDF, видео, закрытый контент

**Проблемы?**
Если бот не смог обработать статью:
• Проверьте, что ссылка открывается в браузере
• Убедитесь, что на странице есть текстовый контент
• Попробуйте другую статью
    """
    
    await update.message.reply_text(help_message)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about"""
    about_message = """
ℹ️ **О боте**

**Версия:** MVP 1.0
**Технологии:**
• Python + python-telegram-bot
• Trafilatura (парсинг)
• Sumy (суммаризация)
• Опционально: HuggingFace API

**Метод суммаризации:**
Используется extractive метод (LSA алгоритм), который выбирает наиболее значимые предложения из оригинального текста.

**Стоимость:**
Полностью бесплатно! 🎉

**Open Source:**
Исходный код доступен для изучения

**Обратная связь:**
Если нашли баг или есть предложения - дайте знать!

Создано как MVP проект для демонстрации возможностей бесплатных инструментов.
    """
    
    await update.message.reply_text(about_message)


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик URL от пользователя"""
    url = update.message.text.strip()
    user = update.effective_user
    
    logger.info(f"Получен URL от пользователя {user.id}: {url}")
    
    # Валидация URL
    if not validate_url(url):
        await update.message.reply_text(
            "❌ **Неверный формат URL**\n\n"
            "Ссылка должна начинаться с http:// или https://\n\n"
            "Пример правильной ссылки:\n"
            "https://www.example.com/article"
        )
        return
    
    # Отправка статусного сообщения с прогресс-баром
    def make_progress_bar(percent: int, text: str) -> str:
        """Создает прогресс-бар"""
        filled = '█' * (percent // 10)
        empty = '░' * (10 - percent // 10)
        return f"{text}\n\n[{filled}{empty}] {percent}%"
    
    status_message = await update.message.reply_text(
        make_progress_bar(0, "⏳ Начинаю обработку...")
    )
    
    try:
        # Шаг 1: Парсинг страницы (0-50%)
        await status_message.edit_text(
            make_progress_bar(10, "📡 Загружаю страницу...")
        )
        
        logger.info(f"Начало парсинга: {url}")
        text = await extract_text_from_url(url)
        
        if not text:
            await status_message.edit_text(
                "❌ **Не удалось извлечь текст**\n\n"
                "Возможные причины:\n"
                "• Страница недоступна\n"
                "• Контент защищен от парсинга\n"
                "• Сайт требует JavaScript\n"
                "• Нет текстового контента\n\n"
                "Попробуйте другую статью."
            )
            logger.warning(f"Не удалось извлечь текст из {url}")
            return
        
        # Прогресс: 50% - текст получен
        await status_message.edit_text(
            make_progress_bar(50, "✅ Текст извлечен!")
        )
        
        # Проверка минимальной длины
        if len(text) < 100:
            await status_message.edit_text(
                "⚠️ **Текст слишком короткий**\n\n"
                f"Извлечено всего {len(text)} символов.\n"
                "Для создания саммари нужно минимум 100 символов.\n\n"
                "Попробуйте статью с большим объемом текста."
            )
            logger.warning(f"Текст слишком короткий: {len(text)} символов")
            return
        
        # Получение статистики о тексте
        text_stats = get_text_stats(text)
        logger.info(f"Извлечено: {text_stats['words']} слов, {text_stats['characters']} символов")
        
        # Прогресс: 60% - начало суммаризации
        await status_message.edit_text(
            make_progress_bar(60, f"🤖 Создаю краткое содержание...\n📄 {text_stats['words']} слов")
        )
        
        # Суммаризация
        logger.info("Начало суммаризации")
        summary = summarize_text(text)
        
        if not summary:
            await status_message.edit_text(
                "❌ **Ошибка суммаризации**\n\n"
                "Не удалось создать краткое содержание.\n"
                "Возможно, текст имеет нестандартную структуру.\n\n"
                "Попробуйте другую статью."
            )
            logger.error(f"Не удалось создать саммари для {url}")
            return
        
        # Прогресс: 90% - саммари готов
        await status_message.edit_text(
            make_progress_bar(90, "📝 Форматирую результат...")
        )
        
        # Получение статистики саммари
        stats = get_summary_stats(text, summary)
        logger.info(
            f"Саммари создан: {stats['summary_words']} слов, "
            f"сжатие {stats['compression_ratio']}%"
        )
        
        # Сохраняем данные для возможного перевода
        context.user_data['last_summary'] = summary
        context.user_data['last_url'] = url
        context.user_data['last_stats'] = stats
        context.user_data['translated_summary'] = None  # Сбросить перевод для нового URL
        
        # Прогресс: 100% - готово
        await status_message.edit_text(
            make_progress_bar(100, "✅ Обработка завершена!")
        )
        
        # Формирование и отправка финального результата
        # Ограничение длины для Telegram (4096 символов)
        max_summary_length = 3500  # Оставляем место для статистики
        if len(summary) > max_summary_length:
            summary = summary[:max_summary_length] + "..."
            logger.info("Саммари обрезан для Telegram")
        
        response = f"""
✅ **Краткое содержание готово!**

📝 **Содержание (English):**
{summary}

━━━━━━━━━━━━━━━━━━━

📊 **Статистика:**
📄 Исходный текст: {stats['original_words']} слов
📝 Краткое содержание: {stats['summary_words']} слов
🗜 Степень сжатия: {stats['compression_ratio']}%

🔗 Источник: {url[:100]}{'...' if len(url) > 100 else ''}
        """
        
        # Добавляем inline кнопки для выбора языка
        keyboard = [
            [
                InlineKeyboardButton("🇷🇺 Перевести на русский", callback_data='translate_ru'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем результат НОВЫМ сообщением, оставляя прогресс-бар видимым
        await update.message.reply_text(response, reply_markup=reply_markup)
        
        logger.info(
            f"Успешно обработан запрос от пользователя {user.id} для URL: {url}"
        )
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке {url}: {e}", exc_info=True)
        await status_message.edit_text(
            "❌ **Произошла ошибка**\n\n"
            "К сожалению, не удалось обработать запрос.\n"
            "Попробуйте позже или используйте другую ссылку.\n\n"
            "Если проблема повторяется, обратитесь к разработчику."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик обычного текста (не URL)"""
    await update.message.reply_text(
        "📎 **Отправьте ссылку на статью**\n\n"
        "Я работаю только со ссылками (URL).\n"
        "Пожалуйста, отправьте полную ссылку на веб-страницу.\n\n"
        "**Пример:**\n"
        "https://en.wikipedia.org/wiki/Machine_learning\n\n"
        "Используйте /help для дополнительной информации."
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'translate_ru':
        # Получаем сохраненные данные
        summary = context.user_data.get('last_summary')
        url = context.user_data.get('last_url')
        stats = context.user_data.get('last_stats')
        translated = context.user_data.get('translated_summary')
        
        if not summary:
            await query.message.reply_text("❌ Данные для перевода не найдены. Отправьте новую ссылку.")
            return
        
        # Если уже переведено - используем кэш и отправляем сразу
        if translated:
            logger.info("Использование кэшированного перевода")
            translated_summary = translated
            
            # Формирование ответа с переводом
            response = f"""
✅ **Краткое содержание (Русский):**

📝 **Содержание:**
{translated_summary}

━━━━━━━━━━━━━━━━━━━

📊 **Статистика:**
📄 Исходный текст: {stats['original_words']} слов
📝 Краткое содержание: {stats['summary_words']} слов
🗜 Степень сжатия: {stats['compression_ratio']}%

🔗 Источник: {url[:100]}{'...' if len(url) > 100 else ''}
            """
            
            await query.message.reply_text(response)
            logger.info("Переведенный саммари (из кэша) отправлен пользователю")
            return
        
        # Показываем статус перевода
        status_msg = await query.message.reply_text("🌍 Перевожу на русский язык...")
        
        try:
            # Перевод
            logger.info("Начало перевода саммари на русский...")
            translated_summary = translate_to_russian(summary)
            
            if not translated_summary:
                await status_msg.edit_text(
                    "❌ **Ошибка перевода**\n\n"
                    "Не удалось перевести текст.\n"
                    "Попробуйте позже или отправьте новую ссылку."
                )
                logger.error("Не удалось перевести саммари")
                return
            
            # Сохраняем перевод в кэш
            context.user_data['translated_summary'] = translated_summary
            logger.info(f"Перевод завершен и закэширован: {len(translated_summary)} символов")
            
        except Exception as e:
            logger.error(f"Ошибка при переводе: {e}", exc_info=True)
            try:
                await status_msg.edit_text(
                    "❌ **Ошибка перевода**\n\n"
                    "К сожалению, не удалось перевести текст.\n"
                    "Попробуйте позже."
                )
            except:
                pass
            return
        
        # Формирование ответа с переводом
        response = f"""
✅ **Краткое содержание (Русский):**

📝 **Содержание:**
{translated_summary}

━━━━━━━━━━━━━━━━━━━

📊 **Статистика:**
📄 Исходный текст: {stats['original_words']} слов
📝 Краткое содержание: {stats['summary_words']} слов
🗜 Степень сжатия: {stats['compression_ratio']}%

🔗 Источник: {url[:100]}{'...' if len(url) > 100 else ''}
        """
        
        try:
            await status_msg.edit_text(response)
            logger.info("Переведенный саммари отправлен пользователю")
        except Exception as e:
            logger.error(f"Ошибка при отправке перевода: {e}")
            # Если не удалось отредактировать - отправим новое сообщение
            await query.message.reply_text(response)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=True)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Произошла непредвиденная ошибка.\n"
            "Пожалуйста, попробуйте позже."
        )


def main():
    """Запуск бота"""
    logger.info("=" * 50)
    logger.info("Запуск Telegram Summarizer Bot")
    logger.info("=" * 50)
    
    # Проверка наличия токена
    if not config.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        logger.error("Создайте .env файл и укажите токен бота")
        return
    
    # Проверка HuggingFace токена
    if config.HF_TOKEN:
        logger.info("HuggingFace токен найден - будет использоваться HF API")
    else:
        logger.info("HuggingFace токен не найден - будет использоваться extractive метод")
    
    # Создание приложения
    logger.info("Инициализация бота...")
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Обработчик inline кнопок (callback queries)
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Обработчик URL (сообщения начинающиеся с http:// или https://)
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^https?://') & ~filters.COMMAND,
            handle_url
        )
    )
    
    # Обработчик обычного текста (не URL)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text
        )
    )
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("🚀 Бот успешно запущен и готов к работе!")
    logger.info("Нажмите Ctrl+C для остановки")
    
    # Запуск polling (получение обновлений от Telegram)
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Игнорировать старые сообщения при запуске
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Остановка бота по запросу пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
