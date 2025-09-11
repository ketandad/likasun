"""Application API routers."""

from fastapi import APIRouter

from . import (
    actors,
    assets,
    auth,
    ingest,
    compliance,
    documents,
    evaluate,
    health,
    reports,
    results,
    rules,
    settings,
    vendors,
)


router = APIRouter()

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(assets.router)
router.include_router(ingest.router)
router.include_router(rules.router)
router.include_router(evaluate.router)
router.include_router(reports.router)
router.include_router(documents.router)
router.include_router(actors.router)
router.include_router(vendors.router)
router.include_router(settings.router)
router.include_router(compliance.router)
router.include_router(results.router)

__all__ = ["router"]

