#!/bin/sh
cd /app
/build/.venv/bin/pyinstaller --clean --onedir --noupx -d noarchive --optimize 2 --strip --bootloader-ignore-signals --hidden-import 'encodings' src/main.py