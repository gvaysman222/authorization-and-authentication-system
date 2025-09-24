#!/usr/bin/env bash
set -e

# режим: serve или test
MODE="${1:-serve}"

if [ "$MODE" = "serve" ]; then
  exec uvicorn main:app --host 0.0.0.0 --port 8000
elif [ "$MODE" = "test" ]; then
  # стартуем сервер в фоне
  uvicorn main:app --host 127.0.0.1 --port 8000 &
  APP_PID=$!

  # ждём и прогоняем тест
  python tests/e2e.py

  # гасим сервер
  kill $APP_PID || true
  wait $APP_PID 2>/dev/null || true
  echo "E2E: SUCCESS"
else
  echo "Unknown mode: $MODE"
  exit 2
fi
