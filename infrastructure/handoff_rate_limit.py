import os
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)

HANDOFF_EXCHANGE_RATE_LIMIT = int(os.getenv("HANDOFF_EXCHANGE_RATE_LIMIT", "30"))
HANDOFF_EXCHANGE_RATE_WINDOW = int(os.getenv("HANDOFF_EXCHANGE_RATE_WINDOW", "60"))


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def check_handoff_exchange_rate_limit(request: Request) -> None:
    ip = _client_ip(request)
    now = time.time()
    window = HANDOFF_EXCHANGE_RATE_WINDOW
    limit = HANDOFF_EXCHANGE_RATE_LIMIT

    with _lock:
        timestamps = _buckets[ip]
        _buckets[ip] = [t for t in timestamps if now - t < window]
        if len(_buckets[ip]) >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Too many requests. Please try again shortly.",
                    "code": "rate_limited",
                },
            )
        _buckets[ip].append(now)
