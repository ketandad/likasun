from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.dependencies import get_db
from app.models import runs as run_m

router = APIRouter(prefix="/evaluate/runs", tags=["evaluate"])

@router.get("/latest")
def get_latest_run(db: Session = Depends(get_db)):
    r = db.execute(
        select(run_m.EvaluationRun).order_by(run_m.EvaluationRun.started_at.desc())
    ).scalars().first()
    if not r:
        return {}
    return {
        "run_id": r.run_id,
        "started_at": r.started_at,
        "finished_at": r.finished_at,
        "controls_count": r.controls_count,
        "assets_count": r.assets_count,
        "results_count": r.results_count,
        "status": r.status,
    }
