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
#//

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes





# Функция для получения ВСЕХ стикеров из всех категорий
def get_all_stickers():
    all_stickers = []
    for category in STICKERS.values():
        all_stickers.extend(category)
    return all_stickers

# Функция для отправки случайного стикера из категории
async def send_sticker(update: Update, sticker_type: str):
    """Отправляет случайный стикер из категории"""
    if STICKERS.get(sticker_type):
        sticker_id = random.choice(STICKERS[sticker_type])
        await update.message.reply_sticker(sticker_id)

# Команда для случайного стикера из всех доступных
async def random_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_stickers = get_all_stickers()
    if all_stickers:
        random_sticker_id = random.choice(all_stickers)
        await update.message.reply_sticker(random_sticker_id)
        await update.message.reply_text("🎲 Вот случайный стикер из всей коллекции!")
    else:
        await update.message.reply_text("😔 Пока нет стикеров в коллекции")
