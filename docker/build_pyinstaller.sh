#!/bin/sh
cd /app
/build/.venv/bin/pyinstaller --clean --onedir --hiddenimport pkg_resources._vendor.jaraco.text --noupx -d noarchive src/main.py