"""
Простой HTTP сервер для Render + Telegram бот
Render требует HTTP endpoint для Web Service
"""
from flask import Flask
import threading
import main

app = Flask(__name__)

# Запуск бота в отдельном потоке
def run_bot():
    main.main()

# Запуск бота при старте сервера
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

@app.route('/')
def home():
    return "Telegram Bot is running! ✅", 200

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}, 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
