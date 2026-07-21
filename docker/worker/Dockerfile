# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# Stage 2: Worker image
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

CMD ["python", "-m", "backend.worker.main"]
