#!/bin/bash

set -euo pipefail

APP_WORKERS=${APP_WORKERS:-1}
CONFIG_FILE=${CONFIG_FILE:-/home/user/app/config/scanners.yml}
PORT=${PORT:-8000}

export CONFIG_FILE

echo "Starting LLM Guard API on port ${PORT} with ${APP_WORKERS} worker(s) and config ${CONFIG_FILE}"

# Uvicorn with workers
exec uvicorn app.app:create_app --factory --host=0.0.0.0 --port="$PORT" --workers="$APP_WORKERS" --forwarded-allow-ips="*" --proxy-headers --timeout-keep-alive="2"
