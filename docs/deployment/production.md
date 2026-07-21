# Production Deployment

## System Requirements

- CPU: 4+ cores
- RAM: 8GB+ recommended
- Disk: 20GB+ SSD
- OS: Linux (Ubuntu 22.04+, RHEL 8+, or equivalent)

## Environment Variables

Generate secure values:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Required:
- `JWT_SECRET_KEY`: 32+ character random string
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

Optional:
- `CORS_ORIGINS`: Comma-separated allowed origins
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- `LOG_FORMAT`: text or json
- `RATE_LIMIT_RPM`: Requests per minute per client

## Docker Compose

```bash
docker compose -f docker-compose.prod.yml up -d
```

## Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/readiness
curl http://localhost:8000/liveness
```

## Backups

PostgreSQL:
```bash
docker compose exec postgres pg_dump -U cloudsentinel cloudsentinel > backup.sql
```

Redis:
```bash
docker compose exec redis redis-cli BGSAVE
```

## Scaling

Horizontal scaling for production:
```bash
docker compose -f docker-compose.prod.yml up -d --scale backend=3 --scale worker=2
```

Load balancer required for multiple backend instances.

## Security

- Bind backend to localhost only in production
- Use strong JWT secret
- Enable HTTPS via reverse proxy
- Regular security updates
- Monitor logs for unauthorized access

## Troubleshooting

Check service status:
```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f worker
```
