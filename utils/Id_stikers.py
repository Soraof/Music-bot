import sqlite3
import logging
import csv
import random

#//
from config.admin import ADMIN_SECRET
from config.Token_s import TOKEN
from config.fortine import FORTUNE_COOKIES
from config.Donat_and_Path import DONATE_LINK, DB_PATH
from config.Stickers import STICKERS
from core.random_stikers import send_sticker, get_all_stickers, random_sticker
from Comand import start, donate, fortune_cookie, stats, stats_top
from core.CSV import init_db,  export_to_csv, handle_link, export_command, my_links, export_data, clear_db
#//

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes




# Функция для получения ID стикеров (постоянная)
async def get_sticker_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.sticker:
        sticker = update.message.sticker
        file_id = sticker.file_id
        await update.message.reply_text(f"🎯 File ID этого стикера:\n`{file_id}`")
    else:
        await update.message.reply_text("Отправь мне стикер чтобы получить его ID")


