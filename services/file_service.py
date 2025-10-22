import os, re
from typing import List
from config import MOVIES_PATH, SERIES_PATH

SAFE_CHARS = r"[^a-zA-Z0-9\-\_\.\ \(\)]"

def sanitize(text: str) -> str:
    text = re.sub(r"[\/:\\|<>?\*\"]", "-", text)
    text = re.sub(SAFE_CHARS, "", text)
    return re.sub(r"\s+", " ", text).strip()

def ensure_dirs(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def create_movie_strm(title: str, url: str) -> str:
    safe_title = sanitize(title)
    movie_dir = os.path.join(MOVIES_PATH, safe_title)
    ensure_dirs(movie_dir)
    strm_path = os.path.join(movie_dir, f"{safe_title}.strm")
    with open(strm_path, "w", encoding="utf-8") as f:
        f.write(url)
    return strm_path

def create_series_strm(series_title: str, season: int, ep_tag: str, url: str) -> str:
    safe_series = sanitize(series_title)
    safe_file = sanitize(ep_tag)
    series_dir = os.path.join(SERIES_PATH, safe_series, f"Season {season:02d}")
    ensure_dirs(series_dir)
    strm_path = os.path.join(series_dir, f"{safe_series} - {safe_file}.strm")
    with open(strm_path, "w", encoding="utf-8") as f:
        f.write(url)
    return strm_path

def list_strm_files(base_paths: List[str]):
    for base in base_paths:
        for root, _, files in os.walk(base):
            for name in files:
                if name.lower().endswith(".strm"):
                    yield os.path.join(root, name)
