from pathlib import Path

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import AppSettings, get_settings
from app.core.errors import AppError
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.generation.router import router as generation_router
from app.modules.model_providers.router import router as provider_router
from app.modules.monitoring.router import router as monitoring_router
from app.modules.payments.router import router as payments_router
from app.modules.points.router import router as points_router
from app.modules.users.router import router as users_router
from app.modules.works.router import router as works_router


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )


configure_logging()


def create_app(settings: AppSettings | None = None) -> FastAPI:
    current_settings = settings or get_settings()
    app = FastAPI(title=current_settings.app_name, version=current_settings.app_version)
    app.state.settings = current_settings

    uploads_path = Path(current_settings.uploads_dir)
    uploads_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

    @app.exception_handler(AppError)
    async def app_error_handler(_request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @app.get("/health", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(points_router, prefix="/api")
    app.include_router(generation_router, prefix="/api")
    app.include_router(works_router, prefix="/api")
    app.include_router(payments_router, prefix="/api")
    app.include_router(admin_router, prefix="/api")
    app.include_router(provider_router, prefix="/api")
    app.include_router(monitoring_router, prefix="/api")
    return app


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


app = create_app()


if __name__ == "__main__":
    main()
