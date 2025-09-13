#!/bin/sh

set -e
python3 init_db.py
exec python3 main.py