#!/bin/sh
cd /app
/build/.venv/bin/pyinstaller --clean --onedir --noupx -d noarchive --optimize 2 --strip src/main.py