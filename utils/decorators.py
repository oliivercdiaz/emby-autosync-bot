from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import ALLOWED_CHAT_ID

def restricted(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        chat = update.effective_chat
        if ALLOWED_CHAT_ID and chat and chat.id != ALLOWED_CHAT_ID:
            if update.effective_message:
                await update.effective_message.reply_text("⛔ Access denied.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
