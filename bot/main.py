import os
import docker
import logging
import time
import threading
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ADMIN_IDS = [int(i.strip()) for i in os.getenv('ADMIN_IDS', '').split(',') if i.strip()]

client = docker.from_env()
MC_CONTAINER = "mc_server"

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data='status'),
         InlineKeyboardButton("👥 Players", callback_data='players')],
        [InlineKeyboardButton("💾 Manual Backup", callback_data='manual_backup')]
    ]
    if is_admin(update.effective_user.id):
        keyboard.append([InlineKeyboardButton("🛠 Admin Panel", callback_data='admin_main')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Minecraft Controller Console:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == 'status':
        try:
            container = client.containers.get(MC_CONTAINER)
            status = container.status
            await query.edit_message_text(f"Server Status: {status.upper()}")
        except: await query.edit_message_text("Server is Offline")

    elif data == 'admin_main' and is_admin(user_id):
        keyboard = [
            [InlineKeyboardButton("⚡ Power", callback_data='admin_power'),
             InlineKeyboardButton("🌍 Map Settings", callback_data='admin_map')],
            [InlineKeyboardButton("⏮ Backups", callback_data='admin_backups')],
            [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]
        ]
        await query.edit_message_text("Admin Settings:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Add logic for power, backups, etc. in full script
    # ... truncated for brevity but logic follows same pattern ...
    else:
        await query.edit_message_text("Processing request...")

def log_watcher(app):
    # Simple tail logic for Player joined/left notifications
    pass

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot started...")
    app.run_polling()
