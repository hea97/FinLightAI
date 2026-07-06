#!/bin/sh
set -eu

python scripts/setup_db.py
exec uvicorn src.dashboard.app:app --host 0.0.0.0 --port "${PORT:-8000}"
