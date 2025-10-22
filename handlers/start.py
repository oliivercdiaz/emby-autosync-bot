from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import restricted

def welcome_text(name: str) -> str:
    return (
        f"👋 <b>Welcome, {name}!</b>\n"
        "🚀 This bot helps you manage your Emby library from Telegram.\n\n"
        "<b>Commands</b>\n"
        "• 🎬 /addmovie <title>\n"
        "• 📺 /addseries <title>\n"
        "• ✍️ /addmanual\n"
        "• 📂 /browse\n"
        "• 📊 /stats\n"
        "• 🧹 /cleanup\n"
        "• 🏓 /ping\n"
        "• ❌ /cancel\n"
    )

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "there"
    await update.effective_message.reply_html(welcome_text(name))

@restricted
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "there"
    await update.effective_message.reply_html(welcome_text(name))
