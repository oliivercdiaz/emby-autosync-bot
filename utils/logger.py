import logging, sys

def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("emby_bot")
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(ch)
    return logger
