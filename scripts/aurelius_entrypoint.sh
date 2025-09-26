#!/bin/sh

set -e
python3 utils/init_db.py
python3 bot/alerts.py &
python3 bot/events.py &
python3 bot/stock.py &
python3 bot/comparions.py &
python3 bot/main.py