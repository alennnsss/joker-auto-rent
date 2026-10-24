FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN pip install .

COPY alembic.ini ./
COPY migrations ./migrations

EXPOSE 8000
# Railway и другие хостинги передают порт в $PORT.
# SEED_ON_START=1 — разово создать админа и демо-авто (там, где нет доступа к shell)
CMD ["sh", "-c", "alembic upgrade head && if [ \"$SEED_ON_START\" = 1 ]; then python -m app.seed; fi && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
