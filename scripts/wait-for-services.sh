#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-8000}"
TIMEOUT="${3:-30}"
INTERVAL=2

echo "Waiting for $HOST:$PORT (timeout: ${TIMEOUT}s)..."

elapsed=0
while [ $elapsed -lt $TIMEOUT ]; do
    if curl -sf "http://$HOST:$PORT/health" > /dev/null 2>&1; then
        echo "Service is ready"
        exit 0
    fi
    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
done

echo "Service did not become ready within ${TIMEOUT}s"
exit 1
