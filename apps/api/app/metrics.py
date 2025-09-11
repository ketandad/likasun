"""Prometheus metrics and metrics endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from .core.config import settings

# Counters
http_requests_total = Counter(
    "raybeam_http_requests_total",
    "Total HTTP requests",
    ["route", "method", "status"],
)

evaluate_runs_total = Counter(
    "raybeam_evaluate_runs_total", "Total evaluation runs"
)

results_total = Counter(
    "raybeam_results_total", "Total evaluation results", ["status"]
)

# Histograms
request_duration_seconds = Histogram(
    "raybeam_request_duration_seconds",
    "HTTP request duration in seconds",
    ["route", "method"],
)

evaluate_duration_seconds = Histogram(
    "raybeam_evaluate_duration_seconds", "Evaluation duration in seconds"
)


router = APIRouter()


@router.get("/metrics")
def metrics() -> Response:
    if not settings.METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="Not found")
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


__all__ = [
    "http_requests_total",
    "evaluate_runs_total",
    "results_total",
    "request_duration_seconds",
    "evaluate_duration_seconds",
    "router",
]
