from fastapi import APIRouter

from . import contracts, access, vendors, residency, policy

router = APIRouter()
router.include_router(contracts.router)
router.include_router(access.router)
router.include_router(vendors.router)
router.include_router(residency.router)
router.include_router(policy.router)

__all__ = ["router"]
