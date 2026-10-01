#!/usr/bin/env bash
# Start the Task Management Microservice.
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8080}"

exec uvicorn main:app --host "$HOST" --port "$PORT"
