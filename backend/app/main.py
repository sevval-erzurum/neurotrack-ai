from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.deps import DB
from app.ml import toddler
from app.routers import assistant, auth, messages, notifications, records, screenings, subjects

API_PREFIX = "/api/v1"

meta_router = APIRouter(tags=["meta"])


@meta_router.get("/health")
def health(db: DB) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@meta_router.get("/model/card")
def model_card() -> dict[str, Any]:
    """Tarama modelinin değerlendirme sonuçları (nested CV), seçilen eşik ve veri kaynağı."""
    _, meta = toddler.load()
    return {k: v for k, v in meta.items() if k != "training_medians"}


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="NeuroTrack AI API",
        version="2.0.0",
        description="Otizm takip ve tarama platformu. Tanı aracı değildir.",
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for router in (
        meta_router,
        auth.router,
        subjects.router,
        records.router,
        screenings.router,
        messages.router,
        notifications.router,
        assistant.router,
    ):
        app.include_router(router, prefix=API_PREFIX)
    return app


app = create_app()
