#!/bin/bash

APP_WORKERS=${APP_WORKERS:-1}
CONFIG_FILE=${CONFIG_FILE:-./config/scanners.yml}
PORT=${PORT:-8000}

# Uvicorn with workers
uvicorn app.app:create_app --host=0.0.0.0 --port="$PORT" --workers="$APP_WORKERS" --forwarded-allow-ips="*" --proxy-headers --timeout-keep-alive="2"
