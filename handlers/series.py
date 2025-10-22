from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from services.tmdb_service import search_tmdb, get_details
from services.file_service import create_series_strm
from services.emby_service import refresh_library, refresh_metadata_recursive
from utils.decorators import restricted

SELECT, GET_TITLE, GET_SEASON, GET_EPISODE, GET_URL, CONFIRM = range(6)

def result_button_text(item: dict) -> str:
    year = (item.get("first_air_date") or "N/A").split("-")[0]
    title = item.get("name", "Unknown")
    return f"📺 {title} ({year})"

def poster_url(path: str) -> str:
    return f"https://image.tmdb.org/t/p/w500{path}"

@restricted
async def addseries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: /addseries <title>")
        return ConversationHandler.END
    query = " ".join(args)
    context.user_data.clear()
    context.user_data["media_type"] = "tv"
    results = await search_tmdb(query, "tv")
    context.user_data["results"] = results or []
    return await ask_selection(update, context)

async def ask_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    results = context.user_data.get("results", [])
    kb = []
    for item in results[:5]:
        kb.append([InlineKeyboardButton(result_button_text(item), callback_data=f"select_{item['id']}")])
    kb.append([InlineKeyboardButton("✍️ Add manually", callback_data="manual")])
    kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    await update.effective_message.reply_text("I found these. Which one?", reply_markup=InlineKeyboardMarkup(kb))
    return SELECT

@restricted
async def on_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    data = q.data
    if data == "manual":
        await q.edit_message_text("Send the TV show title")
        return GET_TITLE
    if data.startswith("select_"):
        tmdb_id = data.split("_",1)[1]
        details = await get_details("tv", tmdb_id)
        if not details:
            await q.edit_message_text("TMDb error. Try again.")
            return ConversationHandler.END
        year = (details.get("first_air_date") or "N/A").split("-")[0]
        title = f"{details.get('name','Unknown')} ({year})"
        context.user_data["series_title"] = title

        rating = details.get("vote_average")
        overview = details.get("overview") or "No synopsis available."
        text = f"<b>{title}</b>\n"
        if rating is not None:
            text += f"⭐️ {rating:.1f}/10\n"
        text += f"📜 {overview}\n\nSend <b>Season</b> number."

        poster = details.get("poster_path")
        if poster:
            await q.message.reply_photo(photo=poster_url(poster), caption=text, parse_mode="HTML")
            await q.delete_message()
        else:
            await q.edit_message_text(text, parse_mode="HTML")

        return GET_SEASON

@restricted
async def get_series_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["series_title"] = update.effective_message.text.strip()
    await update.effective_message.reply_html("OK. Send <b>Season</b> number.")
    return GET_SEASON

@restricted
async def get_season(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    t = update.effective_message.text.strip()
    if not t.isdigit():
        await update.effective_message.reply_text("Season must be a number")
        return GET_SEASON
    context.user_data["season"] = int(t)
    await update.effective_message.reply_html("Now send <b>Episode</b> number.")
    return GET_EPISODE

@restricted
async def get_episode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    t = update.effective_message.text.strip()
    if not t.isdigit():
        await update.effective_message.reply_text("Episode must be a number")
        return GET_EPISODE
    context.user_data["episode"] = int(t)
    tag = f"S{context.user_data['season']:02d}E{context.user_data['episode']:02d}"
    await update.effective_message.reply_html(f"Great. Episode tag: <b>{tag}</b><br>Send the <b>video URL</b>.")
    return GET_URL

def is_valid_url(u: str) -> bool:
    return u.startswith(("http://","https://","magnet:")) and " " not in u

@restricted
async def get_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.effective_message.text.strip()
    if not is_valid_url(url):
        await update.effective_message.reply_text("⚠️ Invalid URL. Try again.")
        return GET_URL
    context.user_data["url"] = url
    tag = f"S{context.user_data['season']:02d}E{context.user_data['episode']:02d}"
    title = context.user_data.get("series_title","(unknown)")
    kb = [[InlineKeyboardButton("✅ Add to Emby", callback_data="ok")],
          [InlineKeyboardButton("✏️ Edit URL", callback_data="edit_url")],
          [InlineKeyboardButton("🔙 Change numbers", callback_data="edit_numbers")],
          [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.effective_message.reply_html(f"Confirm:<br><b>{title}</b> — <b>{tag}</b><br><code>{url}</code>", reply_markup=InlineKeyboardMarkup(kb))
    return CONFIRM

@restricted
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    d = q.data
    if d == "edit_url":
        await q.edit_message_text("Send the new URL.")
        return GET_URL
    if d == "edit_numbers":
        await q.edit_message_text("Send <b>Season</b> number.", parse_mode="HTML")
        return GET_SEASON
    if d == "ok":
        tag = f"S{context.user_data['season']:02d}E{context.user_data['episode']:02d}"
        p = create_series_strm(context.user_data["series_title"], context.user_data["season"], tag, context.user_data["url"])
        await q.edit_message_text(f"✅ STRM created:\n<code>{p}</code>\n🔄 Refreshing Emby library & metadata…", parse_mode="HTML")
        await refresh_library()
        ok = await refresh_metadata_recursive()
        if ok:
            await q.message.reply_text("✅ Metadata updated successfully in Emby!")
        else:
            await q.message.reply_text("⚠️ Library refreshed, but metadata update could not be confirmed.")
    return ConversationHandler.END
