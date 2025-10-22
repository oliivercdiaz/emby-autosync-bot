from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from utils.logger import setup_logger
from utils.errors import error_handler
from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from handlers.start import start, help_cmd
from handlers.movies import addmovie, on_select as movie_select, get_title_then_url as movie_title, get_url as movie_url, confirm_url as movie_confirm, SELECT as M_SELECT, GET_TITLE as M_GET_TITLE, GET_URL as M_GET_URL, CONFIRM_URL as M_CONFIRM_URL
from handlers.series import addseries, on_select as series_select, get_series_title, get_season, get_episode, get_url as series_url, confirm as series_confirm, SELECT as S_SELECT, GET_TITLE as S_GET_TITLE, GET_SEASON as S_GET_SEASON, GET_EPISODE as S_GET_EPISODE, GET_URL as S_GET_URL, CONFIRM as S_CONFIRM
from handlers.manual import addmanual, get_type, movie_title as man_movie_title, series_title as man_series_title, season as man_season, episode as man_episode, url as man_url, ASK_TYPE, MOVIE_TITLE, SERIES_TITLE, SEASON, EPISODE, URL
from handlers.browse import browse, on_browse, BROWSING
from handlers.stats import ping_cmd, stats_cmd
from handlers.cleanup import cleanup, on_cleanup_action, do_delete, MENU, CONFIRM

logger = setup_logger(LOG_LEVEL)

def build_app():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in .env")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    # Basic
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Movies
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addmovie", addmovie)],
        states={
            M_SELECT: [CallbackQueryHandler(movie_select, pattern="^(select_|manual|cancel)$")],
            M_GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, movie_title)],
            M_GET_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, movie_url)],
            M_CONFIRM_URL: [CallbackQueryHandler(movie_confirm, pattern="^(url_yes|url_edit|title_edit|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: u.effective_message.reply_text("Cancelled."))],
        name="movies_flow",
    ))

    # Series
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addseries", addseries)],
        states={
            S_SELECT: [CallbackQueryHandler(series_select, pattern="^(select_|manual|cancel)$")],
            S_GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_series_title)],
            S_GET_SEASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_season)],
            S_GET_EPISODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_episode)],
            S_GET_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, series_url)],
            S_CONFIRM: [CallbackQueryHandler(series_confirm, pattern="^(ok|edit_url|edit_numbers|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: u.effective_message.reply_text("Cancelled."))],
        name="series_flow",
    ))

    # Manual
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addmanual", addmanual)],
        states={
            ASK_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_type)],
            MOVIE_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, man_movie_title)],
            SERIES_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, man_series_title)],
            SEASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, man_season)],
            EPISODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, man_episode)],
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, man_url)],
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: u.effective_message.reply_text("Cancelled."))],
        name="manual_flow",
    ))

    # Browse
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("browse", browse)],
        states={
            BROWSING: [CallbackQueryHandler(on_browse, pattern="^(b_|close|noop)$")],
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: u.effective_message.reply_text("Closed."))],
        name="browse_flow",
    ))

    # Utilities
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))

    # Cleanup (smart)
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("cleanup", cleanup)],
        states={
            MENU: [CallbackQueryHandler(on_cleanup_action, pattern="^(del_empty|del_zero|del_invalid|del_unreach|close)$")],
            CONFIRM: [CallbackQueryHandler(do_delete, pattern="^(confirm_delete)$")],
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: u.effective_message.reply_text("Cleanup cancelled."))],
        name="cleanup_flow",
    ))

    return app

def main():
    app = build_app()
    logger.info("✅ Emby AutoSync Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
