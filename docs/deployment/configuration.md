# Configuration Reference

## Environment Variables

### Core

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_VERSION` | `0.11.0` | Application version |
| `API_VERSION` | `v1` | API version prefix |
| `ENVIRONMENT` | `development` | Environment: development, testing, production |
| `DEBUG` | `false` | Enable debug mode |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///cloudsentinel.db` | Database connection string |
| `DB_POOL_SIZE` | `5` | Connection pool size |
| `DB_MAX_OVERFLOW` | `10` | Max overflow connections |
| `DB_POOL_TIMEOUT` | `30` | Pool timeout seconds |
| `DB_POOL_RECYCLE` | `3600` | Connection recycle seconds |
| `DB_ECHO` | `false` | Echo SQL statements |

### JWT

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | `dev-secret-key-change-in-production` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_RPM` | `100` | Requests per minute |
| `RATE_LIMIT_BURST` | `50` | Burst size |

### CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `*` | Allowed origins |
| `CORS_CREDENTIALS` | `true` | Allow credentials |
| `CORS_METHODS` | `*` | Allowed methods |
| `CORS_HEADERS` | `*` | Allowed headers |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level |
| `LOG_FORMAT` | `text` | text or json |
| `LOG_OUTPUT` | `console` | console or file |
| `LOG_REQUEST_ID` | `true` | Include request ID |
| `LOG_CORRELATION_ID` | `true` | Include correlation ID |

### Metrics

| Variable | Default | Description |
|----------|---------|-------------|
| `METRICS_ENABLED` | `true` | Enable metrics endpoint |
| `METRICS_ENDPOINT` | `/metrics` | Metrics endpoint path |
| `METRICS_SYSTEM` | `true` | Include system metrics |

### Plugins

| Variable | Default | Description |
|----------|---------|-------------|
| `PLUGIN_PATH` | `backend/plugins` | Plugin directory |
| `PLUGIN_AUTO_DISCOVER` | `true` | Auto-discover plugins |
| `PLUGIN_VALIDATE` | `true` | Validate plugins on load |

### Scanning

| Variable | Default | Description |
|----------|---------|-------------|
| `SCAN_ENABLED` | `true` | Enable scanning |
| `SCAN_INTERVAL_MINUTES` | `60` | Scan interval |
| `SCAN_MAX_CONCURRENT` | `3` | Max concurrent scans |
| `SCAN_TIMEOUT_SECONDS` | `300` | Scan timeout |

### Infrastructure

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | - | Redis connection string |
| `WORKER_ENABLED` | `false` | Enable worker |
| `FRONTEND_URL` | - | Frontend URL |

## Profiles

### Development
```bash
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text
```

### Testing
```bash
export ENVIRONMENT=testing
export DATABASE_URL=sqlite:///test.db
export DEBUG=true
```

### Production
```bash
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=WARNING
export LOG_FORMAT=json
export JWT_SECRET_KEY=<secure-random>
```
