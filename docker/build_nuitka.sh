#!/bin/sh
cd /app
PATH=/usr/lib/qt6/bin:$PATH /build/.venv/bin/nuitka --show-progress --plugin-enable=pyqt6 --mode=standalone --output-dir=out src/main.py # --nofollow-imports
