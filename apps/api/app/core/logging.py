"""Request logging middleware emitting structured JSON and metrics."""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .config import settings
from app.metrics import http_requests_total, request_duration_seconds


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.perf_counter()
        user = None
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = payload.get("sub")
            except Exception:  # pragma: no cover - best effort
                user = None
        log_base = {
            "request_id": request_id,
            "user": user,
            "path": request.url.path,
            "method": request.method,
        }
        logging.getLogger("raybeam").info(
            json.dumps(
                {
                    **log_base,
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "level": "info",
                    "msg": "start",
                    "status": 0,
                    "duration_ms": 0,
                }
            )
        )
        response: Response = Response(status_code=500)
        try:
            response = await call_next(request)
        finally:
            duration = time.perf_counter() - start
            route = getattr(request.scope.get("route"), "path", request.url.path)
            http_requests_total.labels(route=route, method=request.method, status=response.status_code).inc()
            request_duration_seconds.labels(route=route, method=request.method).observe(duration)
            log = {
                **log_base,
                "ts": datetime.utcnow().isoformat() + "Z",
                "level": "info",
                "msg": "finish",
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
            logging.getLogger("raybeam").info(json.dumps(log))
        response.headers["X-Request-ID"] = request_id
        return response


__all__ = ["LoggingMiddleware"]
