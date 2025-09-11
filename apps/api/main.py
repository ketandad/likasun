"""Main application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import users_db
from app.routers import router as api_router


app = FastAPI(docs_url="/docs")

if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def seed_admin() -> None:
    """Seed an admin user from environment variables."""
    if settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD:
        users_db.setdefault(
            settings.ADMIN_USERNAME,
            {
                "username": settings.ADMIN_USERNAME,
                "password": settings.ADMIN_PASSWORD,
                "role": "admin",
            },
        )


app.include_router(api_router)

