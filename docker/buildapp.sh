#!/bin/bash
cd /app

# build python bytecode
/build/.venv/bin/nuitka --show-progress --module --output-dir=out src/main.py # --nofollow-imports
# pack bytecode
/build/.venv/bin/pyinstaller --add-data out:lib -D -F src/runner.py