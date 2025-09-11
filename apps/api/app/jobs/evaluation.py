"""Background job helpers for evaluation."""

from __future__ import annotations

import os
from uuid import uuid4

from app.services.evaluator import run_evaluation


def enqueue(
    controls: list[str] | None = None,
    assets: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run evaluation either via queue or inline depending on USE_QUEUE."""
    job_id = str(uuid4())
    if os.getenv("USE_QUEUE", "false").lower() == "true":
        # In a full implementation this would enqueue the job in a task queue
        return run_evaluation(
            job_id=job_id,
            controls_scope=controls,
            assets_scope=assets,
            dry_run=dry_run,
        )
    return run_evaluation(
        job_id=job_id,
        controls_scope=controls,
        assets_scope=assets,
        dry_run=dry_run,
    )


__all__ = ["enqueue"]
