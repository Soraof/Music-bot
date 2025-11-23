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
#//

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes



# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Сначала стикер
    await send_sticker(update, "start")
    
    # Потом текст
    await update.message.reply_text(
        f"Привет, {user.first_name}! 🎵✨\n"
        "Добро пожаловать в бот для сбора музыки на школьную дискотеку! 🎉🎊\n\n"
        "📋 Правила: 📋\n"
        "🎧 • Присылай только ссылки на Яндекс.Музыку\n"
        "🔗 • Одна ссылка = один трек (в одном сообщении)\n"
        "🚫 • Нельзя отправлять одинаковые треки\n"
        "✅ • Можно предлагать сколько угодно разных треков\n"
        "⭐️ • Рекомендуются английские песни\n\n"
        "🎵 Просто отправь мне ссылку на трек из Яндекс.Музыки!\n"
        "⚠️ Музыка без Мата❗️\n\n"
        "🎲 Развлечения:\n"
        "🍪 /fortune - Печенька с предсказанием\n"
        "🎭 /random_sticker - Случайный стикер\n\n"
        "💖 Поддержите проект донатом: /donate\n\n"
        "✨ Используй /stats_top чтобы увидеть топ участников! 🏆\n"
        "🚀 Используй /stats Что бы посмотреть статистику👾\n"
        "🫥Используй /my_links - посмотреть свои отправленные ссылки📃\n"
    )





# Команда /donate
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сначала стикер
    await send_sticker(update, "donate")
    
    # Потом текст
    await update.message.reply_text(
        "💖 Поддержите развитие бота! 💖\n\n"
        "Ваша поддержка помогает улучшать бота и добавлять новые функции! 🚀\n\n"
        f"🔗 Ссылка для доната: {DONATE_LINK}\n\n"
        "🙏 Спасибо за вашу поддержку! Вместе мы сделаем бота лучше! ✨"
    )


    # Команда для печеньки с предсказанием
async def fortune_cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if FORTUNE_COOKIES:
        random_fortune = random.choice(FORTUNE_COOKIES)
        await update.message.reply_text(
            f"🍪 Печенька с предсказанием:\n\n"
            f"✨ {random_fortune}\n\n"
            f"Приятного дня! 🌟"
        )
    else:
        await update.message.reply_text("😔 Печенек временно нет!")


# Команда для статистики
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    
    total_links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    unique_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM links").fetchone()[0]
    
    conn.close()
    
    # Сначала стикер
    await send_sticker(update, "stats")
    
    # Потом текст
    await update.message.reply_text(
        f"📊 Статистика: 📊\n"
        f"🎵 • Всего треков: {total_links}\n"
        f"👥 • Участников: {unique_users}\n\n"
        f"✨ Используй /stats_top чтобы увидеть топ участников! 🏆"
    )


# Команда топа участников
async def stats_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    
    top_users = conn.execute('''
        SELECT first_name, COUNT(*) as track_count 
        FROM links 
        GROUP BY user_id 
        ORDER BY track_count DESC 
        LIMIT 3
    ''').fetchall()
    
    conn.close()
    
    if not top_users:
        await update.message.reply_text("📊 Пока никто не добавил треков! 😔")
        return
    
    # Сначала стикер
    await send_sticker(update, "top")
    
    # Потом текст
    message = "🏆 ТОП 3 УЧАСТНИКОВ🏆\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (first_name, track_count) in enumerate(top_users):
        medal = medals[i] if i < len(medals) else "🎵"
        message += f"{medal} {first_name} - {track_count} треков\n"
    
    message += f"\n🎉 Поздравляем лидеров! 🌟\n"
    message += f"💫 Присоединяйся к ним! 🎵"
    
    await update.message.reply_text(message)