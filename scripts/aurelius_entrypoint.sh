#!/bin/sh

set -e
python3 utils/init_db.py
exec python3 main.py