# Инициализация базы

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
from Comand import start, donate, fortune_cookie
#//

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes




def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  username TEXT,
                  first_name TEXT,
                  link TEXT NOT NULL,
                  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    print("База данных готова! 🗄️")

# Функция для автоматического экспорта в CSV
def export_to_csv():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM links")
    data = cursor.fetchall()
    
    with open('music_links.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'user_id', 'username', 'first_name', 'link', 'submitted_at'])
        writer.writerows(data)
    
    conn.close()
    print("📊 CSV файл обновлен!")


# Обработка ссылок
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    link_text = update.message.text.strip()
    
    # Проверка что это ссылка
    if not (link_text.startswith('http://') or link_text.startswith('https://')):
        await update.message.reply_text("❌ Это не похоже на ссылку! 🤔")
        await send_sticker(update, "error")
        return
    
    # Проверка что это Яндекс.Музыка
    if 'music.yandex.ru' not in link_text:
        await update.message.reply_text("❌ Принимаются только ссылки из Яндекс.Музыки! 🎵")
        await send_sticker(update, "error")
        return
    
    # Проверка на несколько ссылок в одном сообщении
    if link_text.count('http') > 1:
        await update.message.reply_text("❌ Присылай только одну ссылку за раз! 🔗")
        await send_sticker(update, "error")
        return
    
    conn = sqlite3.connect(DB_PATH)
    try:
        # Проверка: Эта ссылка уже есть в базе (у любого пользователя)
        existing_link = conn.execute(
            "SELECT id FROM links WHERE link = ?", (link_text,)
        ).fetchone()
        
        if existing_link:
            await update.message.reply_text("❌ Этот трек уже был добавлен ранее! ⏰")
            await send_sticker(update, "error")
            return
        
        # Сохраняем новую ссылку
        conn.execute(
            "INSERT INTO links (user_id, username, first_name, link) VALUES (?, ?, ?, ?)",
            (user.id, user.username, user.first_name, link_text)
        )
        conn.commit()
        
        # Автоматически обновляем CSV файл
        export_to_csv()
        
        # Сначала стикер успешного добавления
        await send_sticker(update, "add_track")
        
        # Потом текст
        await update.message.reply_text(
            f"✅ Трек добавлен, {user.first_name}! 🎉\n"
            f"Ждем еще треков! 🎧✨\n"
        )
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка при сохранении. Попробуй еще раз. 🔄")
        await send_sticker(update, "error")
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

# Команда для экспорта CSV
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    export_to_csv()
    await update.message.reply_text("📊 CSV файл обновлен! ✅")

# Команда для проверки своих ссылок
async def my_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DB_PATH)
    
    user_links = conn.execute(
        "SELECT link FROM links WHERE user_id = ?", (user.id,)
    ).fetchall()
    
    conn.close()
    
    if not user_links:
        await update.message.reply_text("📭 Ты еще не отправлял ссылки. 😔")
        return
    
    # Сначала стикер
    await send_sticker(update, "my_links")
    
    # Потом текст
    message = f"📋 Твои ссылки ({len(user_links)}): 🎵\n\n"
    for i, (link,) in enumerate(user_links, 1):
        message += f"{i}. {link}\n"
    
    message += f"\n✨ Ты большой молодец! Продолжай в том же духе! 🌟"
    
    await update.message.reply_text(message)


# Экспорт данных с проверкой кода
async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not context.args or context.args[0] != ADMIN_SECRET:
        await update.message.reply_text("❌ Неверный код доступа 🔐")
        await send_sticker(update, "error")
        return
    
    # Сначала стикер
    await send_sticker(update, "admin")
    
    export_to_csv()
    
    await update.message.reply_document(
        document=open('music_links.csv', 'rb'),
        filename='music_links.csv',
        caption='📋 База данных 📊'
    )

# Очистка базы с проверкой кода
async def clear_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not context.args or context.args[0] != ADMIN_SECRET:
        await update.message.reply_text("❌ Неверный код доступа 🔐")
        await send_sticker(update, "error")
        return
    
    if len(context.args) < 2 or context.args[1] != "confirm":
        await update.message.reply_text(
            f"⚠️ Для очистки базы введи: /admin_clear {ADMIN_SECRET} confirm\n"
            "Это действие нельзя отменить! 🚨"
        )
        return
    
    # Сначала стикер
    await send_sticker(update, "admin")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM links")
    conn.commit()
    conn.close()
    
    export_to_csv()
    
    await update.message.reply_text("✅ База данных очищена! 🗑️")