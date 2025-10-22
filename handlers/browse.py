import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from utils.decorators import restricted
from config import MOVIES_PATH, SERIES_PATH

BROWSING = range(1)

@restricted
async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    kb = [
        [InlineKeyboardButton("🎬 Movies", callback_data=f"b_{MOVIES_PATH}")],
        [InlineKeyboardButton("📺 Series", callback_data=f"b_{SERIES_PATH}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await update.effective_message.reply_text("📂 Library Browser", reply_markup=InlineKeyboardMarkup(kb))
    return BROWSING

@restricted
async def on_browse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    d = q.data
    if d == "close":
        await q.edit_message_text("Closed.")
        return ConversationHandler.END
    if d == "noop":
        return BROWSING
    path = d[2:]
    if not (path.startswith(MOVIES_PATH) or path.startswith(SERIES_PATH)):
        await q.edit_message_text("Access denied.")
        return ConversationHandler.END
    items = sorted(os.listdir(path))
    kb = []
    parent = os.path.dirname(path)
    if path not in (MOVIES_PATH, SERIES_PATH):
        kb.append([InlineKeyboardButton("🔙 Back", callback_data=f"b_{parent}")])
    for name in items[:40]:
        full = os.path.join(path, name)
        icon = "📁" if os.path.isdir(full) else "📄"
        kb.append([InlineKeyboardButton(f"{icon} {name}", callback_data=(f"b_{full}" if os.path.isdir(full) else "noop"))])
    kb.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    await q.edit_message_text(f"Browsing:\n<code>{path}</code>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
    return BROWSING
