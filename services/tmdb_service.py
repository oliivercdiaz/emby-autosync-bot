import requests, asyncio
from typing import Optional, List, Dict
from config import TMDB_API_KEY

BASE = "https://api.themoviedb.org/3"
HEADERS = {"Accept": "application/json"}

def _get(url: str, params: dict) -> dict:
    r = requests.get(url, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

async def search_tmdb(query: str, media_type: str) -> Optional[List[Dict]]:
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "en-US"}
    try:
        data = await asyncio.to_thread(_get, f"{BASE}/search/{media_type}", params)
        return data.get("results", [])
    except Exception:
        return None

async def get_details(media_type: str, tmdb_id: str) -> Optional[Dict]:
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    try:
        data = await asyncio.to_thread(_get, f"{BASE}/{media_type}/{tmdb_id}", params)
        return data
    except Exception:
        return None
