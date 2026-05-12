from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.mysql import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"message": "AI Literacy Tutor backend is running."}

    @app.on_event("startup")
    def startup_event() -> None:
        init_db()

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
