# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# Stage 2: Production image
FROM python:3.13-slim

WORKDIR /app

RUN groupadd -r cloudsentinel && useradd -r -g cloudsentinel cloudsentinel

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps /wheels/* && rm -rf /wheels

COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

RUN chown -R cloudsentinel:cloudsentinel /app

USER cloudsentinel

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
