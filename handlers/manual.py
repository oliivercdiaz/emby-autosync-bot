from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from utils.decorators import restricted
from services.file_service import create_movie_strm, create_series_strm
from services.emby_service import refresh_library, refresh_metadata_recursive

ASK_TYPE, MOVIE_TITLE, SERIES_TITLE, SEASON, EPISODE, URL = range(6)

@restricted
async def addmanual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_message.reply_text("Manual mode. Send 'movie' or 'series'")
    return ASK_TYPE

@restricted
async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    t = update.effective_message.text.strip().lower()
    if t not in ("movie","series"):
        await update.effective_message.reply_text("Please send 'movie' or 'series'")
        return ASK_TYPE
    context.user_data["type"] = t
    if t == "movie":
        await update.effective_message.reply_text("Send the full movie title")
        return MOVIE_TITLE
    else:
        await update.effective_message.reply_text("Send the TV show title")
        return SERIES_TITLE

@restricted
async def movie_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["title"] = update.effective_message.text.strip()
    await update.effective_message.reply_text("Now send the video URL")
    return URL

@restricted
async def series_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["series_title"] = update.effective_message.text.strip()
    await update.effective_message.reply_text("Send Season number")
    return SEASON

@restricted
async def season(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    v = update.effective_message.text.strip()
    if not v.isdigit():
        await update.effective_message.reply_text("Season must be a number")
        return SEASON
    context.user_data["season"] = int(v)
    await update.effective_message.reply_text("Send Episode number")
    return EPISODE

@restricted
async def episode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    v = update.effective_message.text.strip()
    if not v.isdigit():
        await update.effective_message.reply_text("Episode must be a number")
        return EPISODE
    context.user_data["episode"] = int(v)
    await update.effective_message.reply_text("Send the video URL")
    return URL

def is_valid_url(u: str) -> bool:
    return u.startswith(("http://","https://","magnet:")) and " " not in u

@restricted
async def url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    u = update.effective_message.text.strip()
    if not is_valid_url(u):
        await update.effective_message.reply_text("⚠️ Invalid URL. Try again.")
        return URL
    if context.user_data.get("type") == "movie":
        p = create_movie_strm(context.user_data["title"], u)
    else:
        tag = f"S{context.user_data['season']:02d}E{context.user_data['episode']:02d}"
        p = create_series_strm(context.user_data["series_title"], context.user_data["season"], tag, u)
    await update.effective_message.reply_text(f"✅ STRM created:\n{p}\n🔄 Refreshing Emby library & metadata…")
    await refresh_library()
    ok = await refresh_metadata_recursive()
    await update.effective_message.reply_text("✅ Metadata updated successfully in Emby!" if ok else "⚠️ Library refreshed, but metadata update could not be confirmed.")
    return ConversationHandler.END
