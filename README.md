# 🎬 Emby AutoSync Bot — Final PRO

A smart **Telegram** assistant for **Emby**: search titles on **TMDb**, create safe `.strm` files, **show posters & synopsis**, and **refresh metadata** automatically so your library stays up to date — hands‑free.

> Production‑grade, fully async (PTB v21), Docker/systemd ready.

---

## ✨ Features

- **/addmovie `<title>`** → TMDb results → detailed view (poster, rating, synopsis) → confirm → create STRM → **refresh Emby & metadata**
- **/addseries `<title>`** → TMDb → season/episode → confirm → STRM → **refresh Emby & metadata**
- **/addmanual** → manual flow (movie/series)
- **/browse** → quick folder browser (Movies/Series)
- **/ping** & **/stats** → Emby health and counts
- **/cleanup** (smart) → empty dirs, zero‑byte `.strm`, invalid/unreachable URLs — with confirmation
- **/start** → personalized welcome with user’s name

**Safety:** access restricted via `ALLOWED_CHAT_ID`. Filenames sanitized. Network calls with timeouts and error handling.

---

## 🧱 Structure
```
emby-autosync-bot/
├─ bot.py
├─ config.py
├─ .env.example
├─ requirements.txt
├─ handlers/
│  ├─ start.py
│  ├─ movies.py
│  ├─ series.py
│  ├─ manual.py
│  ├─ browse.py
│  ├─ stats.py
│  └─ cleanup.py
├─ services/
│  ├─ tmdb_service.py
│  ├─ emby_service.py
│  ├─ file_service.py
│  └─ cleanup_service.py
├─ utils/
│  ├─ logger.py
│  ├─ decorators.py
│  └─ errors.py
├─ systemd/
│  └─ emby-autosync-bot.service
└─ docker/
   ├─ Dockerfile
   └─ docker-compose.yml
```

---

## ⚙️ Setup
```bash
cp .env.example .env
# Fill tokens, Emby URL and STRM paths
pip install -r requirements.txt
python3 bot.py
```

### Docker
```bash
cd docker
docker compose build
docker compose up -d
```

### systemd
```bash
sudo cp systemd/emby-autosync-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable emby-autosync-bot
sudo systemctl start emby-autosync-bot
```

---

## Emby‑friendly naming (auto‑match ready)
- Movies → `Title (Year)/Title (Year).strm`
- Series → `Series (Year)/Season XX/Series (Year) - SXXEXX.strm`

---

## Author
Developed by **Oliver Corral Díaz** — IT & Network Specialist

---

## License
MIT
