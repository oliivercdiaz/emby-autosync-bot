from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import restricted
from services.emby_service import stats, ping

@restricted
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok = await ping()
    await update.effective_message.reply_text("✅ Emby OK" if ok else "❌ Emby unreachable")

@restricted
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = await stats()
    if not s:
        await update.effective_message.reply_text("Could not fetch stats.")
        return
    msg = (
        "📊 <b>Emby Stats</b>\n"
        f"• Movies: <b>{s.get('MovieCount','?')}</b>\n"
        f"• Series: <b>{s.get('SeriesCount','?')}</b>\n"
        f"• Episodes: <b>{s.get('EpisodeCount','?')}</b>\n"
        f"• Tracks: <b>{s.get('SongCount','?')}</b>"
    )
    await update.effective_message.reply_html(msg)
