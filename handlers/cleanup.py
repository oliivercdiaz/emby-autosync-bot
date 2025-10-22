from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from utils.decorators import restricted
from services.cleanup_service import scan, delete_paths
from config import CLEANUP_MODE

MENU, CONFIRM = range(2)

def format_report(rep: dict) -> str:
    def c(k): return len(rep.get(k, []))
    return (
        "🧹 <b>Cleanup Report</b>\n"
        f"• Empty folders: <b>{c('empty_dirs')}</b>\n"
        f"• Zero-byte .strm: <b>{c('zero_byte_strm')}</b>\n"
        f"• Invalid URL .strm: <b>{c('invalid_url_strm')}</b>\n"
        f"• Unreachable URL .strm: <b>{c('unreachable_url_strm')}</b>\n"
        f"Mode: <code>{CLEANUP_MODE}</code>"
    )

@restricted
async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    rep = scan()
    context.user_data["cleanup_report"] = rep
    kb = [
        [InlineKeyboardButton("🗑️ Delete empty folders", callback_data="del_empty")],
        [InlineKeyboardButton("🗑️ Delete zero-byte .strm", callback_data="del_zero")],
        [InlineKeyboardButton("🗑️ Delete invalid URL .strm", callback_data="del_invalid")],
        [InlineKeyboardButton("🗑️ Delete unreachable URL .strm", callback_data="del_unreach")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await update.effective_message.reply_html(format_report(rep), reply_markup=InlineKeyboardMarkup(kb))
    return MENU

@restricted
async def on_cleanup_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    data = q.data
    rep = context.user_data.get("cleanup_report", {})
    mapping = {
        "del_empty": "empty_dirs",
        "del_zero": "zero_byte_strm",
        "del_invalid": "invalid_url_strm",
        "del_unreach": "unreachable_url_strm",
    }
    if data == "close":
        await q.edit_message_text("Cleanup closed.")
        return ConversationHandler.END
    if data in mapping:
        key = mapping[data]
        paths = rep.get(key, [])
        if not paths:
            await q.edit_message_text("Nothing to delete for that category.")
            return ConversationHandler.END
        context.user_data["to_delete"] = paths
        await q.edit_message_text(
            f"⚠️ Are you sure you want to delete <b>{len(paths)}</b> item(s) from <code>{key}</code>?",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes, delete", callback_data="confirm_delete")],
                [InlineKeyboardButton("❌ Cancel", callback_data="close")]
            ])
        )
        return CONFIRM
    return ConversationHandler.END

@restricted
async def do_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    paths = context.user_data.get("to_delete", [])
    deleted = delete_paths(paths)
    await q.edit_message_text(f"✅ Deleted {deleted} item(s).")
    return ConversationHandler.END
