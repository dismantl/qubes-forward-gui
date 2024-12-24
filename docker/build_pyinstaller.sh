#!/bin/sh
cd /app
/build/.venv/bin/pyinstaller --clean --onedir --noupx -d noarchive --optimize 2 --strip --bootloader-ignore-signals src/main.py