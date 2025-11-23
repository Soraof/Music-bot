import sqlite3
import logging
import csv
import random

#//
from config.Admin import ADMIN_SECRET
from config.Token_s import TOKEN
from config.Fortine import FORTUNE_COOKIES
from config.Donat_and_Path import DONATE_LINK, DB_PATH
from config.Stickers import STICKERS
from core.Random_stikers import send_sticker, get_all_stickers, random_sticker
from core.Comand import start, donate, fortune_cookie, stats, stats_top
from core.CSV import init_db,  export_to_csv, handle_link, export_command, my_links, export_data, clear_db
from utils.Id_stikers import get_sticker_id
from core.Admin_panel import admin
#//

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Включаем логирование чтобы видеть ошибки
logging.basicConfig(level=logging.INFO)


# Главная функция
def main():
    init_db()
    
    app = Application.builder().token(TOKEN).build()

    
    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("donate", donate))
    app.add_handler(CommandHandler("fortune", fortune_cookie))
    app.add_handler(CommandHandler("random_sticker", random_sticker))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("my_links", my_links))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("stats_top", stats_top))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("admin_export", export_data))
    app.add_handler(CommandHandler("admin_clear", clear_db))
    app.add_handler(CommandHandler("get_id", get_sticker_id))
    
    # Обработчики сообщений
    app.add_handler(MessageHandler(filters.Sticker.ALL, get_sticker_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    print("🎵 Бот запущен! Нажми Ctrl+C чтобы остановить 🎵")
    app.run_polling()

if __name__ == "__main__":
    main()