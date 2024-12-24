#!/bin/sh
cd /app
PATH=/usr/lib/qt6/bin:$PATH python3 -m nuitka --show-progress --static-libpython=yes --module --plugin-enable=pyqt6 --output-dir=out src/main.py # --nofollow-imports
