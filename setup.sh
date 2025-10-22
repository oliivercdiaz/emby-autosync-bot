#!/usr/bin/env bash
set -e
echo ">> Emby AutoSync Bot — Quick Setup"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env. Edit it with your tokens and paths."
fi
pip3 install -r requirements.txt
echo "Starting bot..."
python3 bot.py
