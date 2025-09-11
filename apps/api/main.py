"""Main application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import users_db
from app.core.license import load_license, check_seats
from app.core.logging import LoggingMiddleware
from app.metrics import router as metrics_router
from app.routers import router as api_router


app = FastAPI(title="Raybeam API", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def bootstrap() -> None:
    """Load license and seed admin user."""
    load_license()
    if settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD:
        check_seats(len(users_db) + 1)
        users_db.setdefault(
            settings.ADMIN_USERNAME,
            {
                "username": settings.ADMIN_USERNAME,
                "password": settings.ADMIN_PASSWORD,
                "role": "admin",
            },
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


app.add_middleware(LoggingMiddleware)
app.include_router(api_router)
app.include_router(metrics_router)

