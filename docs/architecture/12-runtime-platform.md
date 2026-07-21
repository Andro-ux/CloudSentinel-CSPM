# Runtime Platform Architecture

## Overview

The runtime platform manages CloudSentinel's lifecycle, configuration, health, and observability.

## Architecture

```
┌─────────────────────────────────────────┐
│             Runtime Manager             │
├─────────────────────────────────────────┤
│  Configuration ───► Validated Config    │
│  Logging ──────────► Structured Logs    │
│  Lifecycle ────────► Startup/Shutdown   │
│  Health ───────────► Health Checks      │
│  Readiness ────────► Dependency Checks  │
│  Metrics ──────────► Observability      │
└─────────────────────────────────────────┘
```

## Lifecycle

### Startup Sequence

1. Load environment variables
2. Validate configuration
3. Configure structured logging
4. Initialize database connections
5. Initialize Redis connections
6. Discover and validate plugins
7. Register health checks
8. Register readiness checks
9. Start API server
10. Start worker (if enabled)

### Shutdown Sequence

1. Stop accepting new requests
2. Complete in-flight requests
3. Stop scheduled tasks
4. Close database connections
5. Close Redis connections
6. Flush logs
7. Exit

## Configuration Flow

```
.env file
    ↓
dotenv.load_dotenv()
    ↓
ConfigurationLoader.load()
    ↓
RuntimeConfiguration (immutable)
    ↓
RuntimeManager
    ↓
All subsystems
```

## Health System

### Health Endpoint (`/health`)

Indicates application health:
- Database connectivity
- Redis connectivity
- Plugin manager status
- API status

### Readiness Endpoint (`/readiness`)

Indicates startup readiness:
- Configuration loaded
- Plugins discovered
- Dependencies connected
- Startup complete

### Liveness Endpoint (`/liveness`)

Indicates application liveness:
- Process alive
- Event loop running

## Logging Architecture

Every log entry includes:
- `timestamp`: ISO 8601 UTC
- `level`: DEBUG, INFO, WARNING, ERROR
- `component`: Logger name
- `message`: Log message
- `request_id`: Per-request ID
- `correlation_id`: Per-request correlation ID

JSON format for production, text format for development.

## Metrics

Exposed at `/metrics`:
- `scan_count`: Total scans performed
- `api_requests`: Total API requests
- `avg_scan_time_seconds`: Average scan duration
- `plugin_count`: Registered plugins
- `assets_processed`: Assets processed
- `findings_generated`: Findings generated
- `risk_calculations`: Risk calculations performed
- `auth_requests`: Authentication requests
- `rate_limit_hits`: Rate limit violations
- `uptime_seconds`: Application uptime

## Docker Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Docker Compose                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │  Frontend  │  │  Backend   │  │      Worker          │   │
│  │  Nginx     │  │  FastAPI   │  │  Python Worker       │   │
│  │  Port 80   │  │  Port 8000 │  │                      │   │
│  └─────┬──────┘  └─────┬──────┘  └──────────┬───────────┘   │
│        │               │                     │                │
│  ┌─────┴───────────────┴─────────────────────┴───────────┐   │
│  │                  Internal Network                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌────────────┐  ┌────────────┐                             │
│  │ PostgreSQL │  │   Redis    │                             │
│  │  Port 5432 │  │  Port 6379 │                             │
│  └────────────┘  └────────────┘                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Extension Points

Future:
- Kubernetes Helm charts
- OpenTelemetry tracing
- External secrets managers
- Horizontal scaling
- Distributed scanning
