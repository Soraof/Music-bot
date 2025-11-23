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
from utils.id_stikers import get_sticker_id
#//

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes





# АДМИН-ПАНЕЛЬ
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not context.args or context.args[0] != ADMIN_SECRET:
        await update.message.reply_text("❌ Неверный код доступа 🔐")
        await send_sticker(update, "error")
        return
    
    # Сначала стикер
    await send_sticker(update, "admin")
    
    conn = sqlite3.connect(DB_PATH)
    
    total_links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    unique_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM links").fetchone()[0]
    
    top_users = conn.execute('''
        SELECT first_name, COUNT(*) as track_count 
        FROM links 
        GROUP BY user_id 
        ORDER BY track_count DESC 
        LIMIT 5
    ''').fetchall()
    
    recent_links = conn.execute(
        "SELECT first_name, link, submitted_at FROM links ORDER BY id DESC LIMIT 10"
    ).fetchall()
    
    conn.close()
    
    # Потом текст
    message = f"🔐 АДМИН-ПАНЕЛЬ🔐\n\n"
    message += f"📊 Статистика:\n"
    message += f"🎵 • Всего треков: {total_links}\n"
    message += f"👥 • Участников: {unique_users}\n\n"
    
    message += "🏆 Топ участников:\n"
    for first_name, track_count in top_users:
        message += f"• {first_name}: {track_count} треков\n"
    
    message += "\n🆕 Последние треки:\n"
    for first_name, link, submitted_at in recent_links:
        short_link = link[:50] + "..." if len(link) > 50 else link
        message += f"• {first_name}: {short_link}\n"
    
    message += f"\n⚙️ Команды:\n"
    message += f"/admin_export - скачать CSV (требует код)\n"
    message += f"/admin_clear - очистить базу (требует код)\n"
    
    await update.message.reply_text(message)