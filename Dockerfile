# ---- base ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# системные утилиты (curl для ожидания/диагностики)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# зависимости
COPY requirements.txt ./
RUN pip install -r requirements.txt

# код приложения
COPY app ./app
COPY main.py ./
COPY tests ./tests
COPY docker/entrypoint.sh /app/entrypoint.sh

# порты/переменные (можно переопределить при run)
ENV DATABASE_URL=sqlite:////app/app.db \
    TOKEN_TTL_HOURS=24 \
    ADMIN_EMAIL=admin@example.com \
    ADMIN_PASSWORD=admin123

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["serve"]
