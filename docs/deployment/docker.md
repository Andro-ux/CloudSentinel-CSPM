# Docker Deployment

## Overview

CloudSentinel is deployed using Docker Compose for development and production environments.

## Prerequisites

- Docker Engine 24+
- Docker Compose 2.20+
- 4GB RAM minimum
- 10GB disk space

## Quick Start

```bash
git clone <repository>
cd CloudSentinel
cp .env.example .env
./scripts/bootstrap.sh
```

For Windows PowerShell:
```powershell
git clone <repository>
cd CloudSentinel
Copy-Item .env.example .env
.\scripts\bootstrap.ps1
```

## Services

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| backend | cloudsentinel-backend | 8000 | FastAPI application |
| worker | cloudsentinel-worker | - | Background scan worker |
| frontend | cloudsentinel-frontend | 80 | React dashboard |
| postgres | postgres:16-alpine | 5432 | PostgreSQL database |
| redis | redis:7-alpine | 6379 | Redis cache/broker |

## Development

```bash
docker compose -f docker-compose.dev.yml up
```

Features:
- Hot reloading via volume mounts
- Debug logging
- CORS enabled for localhost

## Production

```bash
docker compose -f docker-compose.prod.yml up
```

Features:
- Non-root users
- Resource limits
- JSON logging
- Security hardening
- Internal networks only

## Configuration

See `.env.example` for all available options.

Key production settings:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `JWT_SECRET_KEY=<secure-random-key>`
- `LOG_FORMAT=json`

## Scaling

```bash
docker compose -f docker-compose.prod.yml up -d --scale backend=3 --scale worker=2
```

## Monitoring

- Health: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`
- Logs: `docker compose logs -f`
