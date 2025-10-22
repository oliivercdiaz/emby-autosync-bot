import requests, asyncio
from typing import Optional, Dict
from config import EMBY_API_KEY, EMBY_URL

HEADERS = {"X-Emby-Token": EMBY_API_KEY}

def _post(path: str) -> requests.Response:
    return requests.post(f"{EMBY_URL}{path}", headers=HEADERS, timeout=15)

def _get(path: str) -> requests.Response:
    return requests.get(f"{EMBY_URL}{path}", headers=HEADERS, timeout=15)

async def refresh_library() -> bool:
    try:
        r = await asyncio.to_thread(_post, "/Library/Refresh")
        r.raise_for_status()
        return True
    except Exception:
        return False

async def refresh_metadata_recursive() -> bool:
    try:
        r = await asyncio.to_thread(_post, "/Items/Library/Refresh?Recursive=true")
        # Some Emby builds return 204 No Content, others 200 OK
        return r.status_code in (200, 204)
    except Exception:
        return False

async def ping() -> bool:
    try:
        r = await asyncio.to_thread(_get, "/System/Ping")
        return r.status_code == 200
    except Exception:
        return False

async def stats() -> Optional[Dict[str,int]]:
    try:
        r = await asyncio.to_thread(_get, "/Items/Counts")
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
