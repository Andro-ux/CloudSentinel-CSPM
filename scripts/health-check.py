#!/usr/bin/env python3
"""Health check script for CloudSentinel services."""

import sys
import time
import urllib.request
import urllib.error
import argparse
import json


def check_health(url: str, timeout: int = 30, interval: int = 2) -> bool:
    """Check if a service is healthy."""
    elapsed = 0
    while elapsed < timeout:
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    status = data.get("status", "unknown")
                    print(f"Service healthy: {status}")
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError):
            pass
        time.sleep(interval)
        elapsed += interval
    return False


def main():
    parser = argparse.ArgumentParser(description="CloudSentinel health check")
    parser.add_argument("--url", default="http://localhost:8000/health", help="Health endpoint URL")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--interval", type=int, default=2, help="Check interval in seconds")
    args = parser.parse_args()

    if check_health(args.url, args.timeout, args.interval):
        print("Health check passed")
        sys.exit(0)
    else:
        print("Health check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
