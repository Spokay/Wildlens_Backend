#!/bin/sh
export APP_PORT="${APP_PORT:-$FALLBACK_PORT}"

exec python -m app.main