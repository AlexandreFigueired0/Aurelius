#!/bin/sh

set -e
python3 utils/init_db.py
python3 -m bot.main