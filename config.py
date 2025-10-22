import os
from dotenv import load_dotenv
load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_ID = int(os.getenv("ALLOWED_CHAT_ID", "0"))

# TMDb
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

# Emby
EMBY_API_KEY = os.getenv("EMBY_API_KEY", "")
EMBY_URL = os.getenv("EMBY_URL", "http://localhost:8096")

# Paths (STRM destinations)
MOVIES_PATH = os.getenv("MOVIES_PATH", "/home/oliver/emby/media/movies")
SERIES_PATH = os.getenv("SERIES_PATH", "/home/oliver/emby/media/tvshows")

# Cleanup
CLEANUP_MODE = os.getenv("CLEANUP_MODE", "smart")  # safe | smart | strict
ENABLE_HEAD_CHECK = os.getenv("ENABLE_HEAD_CHECK", "false").lower() == "true"
HEAD_TIMEOUT = int(os.getenv("HEAD_TIMEOUT", "5"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
