from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from services.tmdb_service import search_tmdb, get_details
from services.file_service import create_movie_strm
from services.emby_service import refresh_library, refresh_metadata_recursive
from utils.decorators import restricted

SELECT, GET_TITLE, GET_URL, CONFIRM_URL = range(4)

def result_button_text(item: dict) -> str:
    year = (item.get("release_date") or "N/A").split("-")[0]
    title = item.get("title", "Unknown")
    return f"🎬 {title} ({year})"

def poster_url(path: str) -> str:
    return f"https://image.tmdb.org/t/p/w500{path}"

@restricted
async def addmovie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: /addmovie <title>")
        return ConversationHandler.END
    query = " ".join(args)
    context.user_data.clear()
    context.user_data["media_type"] = "movie"
    results = await search_tmdb(query, "movie")
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
        await q.edit_message_text("Send the full movie title, e.g. Interstellar (2014)")
        return GET_TITLE
    if data.startswith("select_"):
        tmdb_id = data.split("_",1)[1]
        details = await get_details("movie", tmdb_id)
        if not details:
            await q.edit_message_text("TMDb error. Try again.")
            return ConversationHandler.END
        year = (details.get("release_date") or "N/A").split("-")[0]
        title = f"{details.get('title','Unknown')} ({year})"
        context.user_data["final_title"] = title

        # Build message with rating and overview
        rating = details.get("vote_average")
        overview = details.get("overview") or "No synopsis available."
        text = f"<b>{title}</b>\n"
        if rating is not None:
            text += f"⭐️ {rating:.1f}/10\n"
        text += f"📜 {overview}\n\nSend the <b>video URL</b> to create the STRM file."

        # Send poster if exists
        poster = details.get("poster_path")
        if poster:
            await q.message.reply_photo(photo=poster_url(poster), caption=text, parse_mode="HTML")
            await q.delete_message()
        else:
            await q.edit_message_text(text, parse_mode="HTML")

        return GET_URL

@restricted
async def get_title_then_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["final_title"] = update.effective_message.text.strip()
    await update.effective_message.reply_html(f"Title set to <b>{context.user_data['final_title']}</b>.<br>Now send the <b>video URL</b>.")
    return GET_URL

def is_valid_url(u: str) -> bool:
    return u.startswith(("http://","https://","magnet:")) and " " not in u

@restricted
async def get_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.effective_message.text.strip()
    if not is_valid_url(url):
        await update.effective_message.reply_text("⚠️ Invalid URL. Try again (http/https or magnet).")
        return GET_URL
    context.user_data["url"] = url
    title = context.user_data.get("final_title","(unknown)")
    kb = [[InlineKeyboardButton("✅ Add to Emby", callback_data="url_yes")],
          [InlineKeyboardButton("✏️ Edit URL", callback_data="url_edit")],
          [InlineKeyboardButton("🔙 Change title", callback_data="title_edit")],
          [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.effective_message.reply_html(f"Confirm:<br><b>Title</b>: {title}<br><b>URL</b>: <code>{url}</code>", reply_markup=InlineKeyboardMarkup(kb))
    return CONFIRM_URL

@restricted
async def confirm_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    data = q.data
    if data == "url_edit":
        await q.edit_message_text("Send the new URL.")
        return GET_URL
    if data == "title_edit":
        await q.edit_message_text("Send the new title.")
        return GET_TITLE
    if data == "url_yes":
        path = create_movie_strm(context.user_data["final_title"], context.user_data["url"])
        await q.edit_message_text(f"✅ STRM created:\n<code>{path}</code>\n🔄 Refreshing Emby library & metadata…", parse_mode="HTML")
        await refresh_library()
        ok = await refresh_metadata_recursive()
        if ok:
            await q.message.reply_text("✅ Metadata updated successfully in Emby!")
        else:
            await q.message.reply_text("⚠️ Library refreshed, but metadata update could not be confirmed.")
    return ConversationHandler.END
