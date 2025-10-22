import os, requests
from typing import Dict, List
from config import MOVIES_PATH, SERIES_PATH, ENABLE_HEAD_CHECK, HEAD_TIMEOUT
from services.file_service import list_strm_files

def is_valid_url(url: str) -> bool:
    return url.startswith(("http://","https://","magnet:")) and " " not in url

def try_head(url: str) -> bool:
    try:
        h = requests.head(url, timeout=HEAD_TIMEOUT, allow_redirects=True)
        return h.status_code < 400
    except Exception:
        return False

def scan() -> Dict[str, List[str]]:
    report = {
        "empty_dirs": [],
        "zero_byte_strm": [],
        "invalid_url_strm": [],
        "unreachable_url_strm": [],
    }
    # empty dirs
    for base in [MOVIES_PATH, SERIES_PATH]:
        for root, dirs, files in os.walk(base):
            if not dirs and not files:
                report["empty_dirs"].append(root)

    # strm checks
    for path in list_strm_files([MOVIES_PATH, SERIES_PATH]):
        try:
            size = os.path.getsize(path)
        except Exception:
            size = 0
        if size == 0:
            report["zero_byte_strm"].append(path)
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                url = f.read().strip()
        except Exception:
            url = ""
        if not is_valid_url(url):
            report["invalid_url_strm"].append(path)
        elif ENABLE_HEAD_CHECK and url.startswith(("http://","https://")):
            if not try_head(url):
                report["unreachable_url_strm"].append(path)

    return report

def delete_paths(paths: List[str]) -> int:
    count = 0
    for p in paths:
        try:
            if os.path.isdir(p):
                os.rmdir(p)
                count += 1
            elif os.path.isfile(p):
                os.remove(p)
                count += 1
        except Exception:
            pass
    return count
