#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "CloudSentinel Bootstrap Script"
echo "=========================================="

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "ERROR: $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "Checking dependencies..."
check_command docker
check_command docker compose
check_command python3
check_command pip
echo "Dependencies OK"

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Creating .env from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "Created .env file. Please review and update it with your settings."
else
    echo ".env file already exists."
fi

if [ ! -d "$PROJECT_ROOT/backend/plugins" ]; then
    echo "Creating plugins directory..."
    mkdir -p "$PROJECT_ROOT/backend/plugins"
fi

if [ ! -d "$PROJECT_ROOT/logs" ]; then
    echo "Creating logs directory..."
    mkdir -p "$PROJECT_ROOT/logs"
fi

if [ ! -d "$PROJECT_ROOT/data" ]; then
    echo "Creating data directory..."
    mkdir -p "$PROJECT_ROOT/data"
fi

echo ""
echo "Building Docker images..."
cd "$PROJECT_ROOT"
docker compose build

echo ""
echo "Starting services..."
docker compose up -d postgres redis

echo ""
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U cloudsentinel &> /dev/null; then
        echo "PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: PostgreSQL did not become ready in time"
        exit 1
    fi
    sleep 2
done

echo ""
echo "Waiting for Redis..."
for i in {1..30}; do
    if docker compose exec -T redis redis-cli ping &> /dev/null; then
        echo "Redis is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: Redis did not become ready in time"
        exit 1
    fi
    sleep 2
done

echo ""
echo "Running database migrations..."
docker compose exec -T backend python -c "from backend.database.session import Base, engine; Base.metadata.create_all(bind=engine)" || true

echo ""
echo "Starting all services..."
docker compose up -d

echo ""
echo "Waiting for backend health check..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "WARNING: Backend health check did not pass in time. Check logs with: docker compose logs backend"
        exit 1
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo "CloudSentinel is running!"
echo "=========================================="
echo "API Docs: http://localhost:8000/docs"
echo "Health:   http://localhost:8000/health"
echo "Metrics:  http://localhost:8000/metrics"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop:     docker compose down"
echo "=========================================="
