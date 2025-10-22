from telegram.ext import ContextTypes
from telegram import Update
from utils.logger import setup_logger
logger = setup_logger()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update", exc_info=context.error)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Unexpected error. Try again.")
    except Exception:
        pass
