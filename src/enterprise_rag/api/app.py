from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from enterprise_rag.api.health import router as health_router
from enterprise_rag.api.users import router as users_router
from enterprise_rag.core.config import get_settings
from enterprise_rag.core.logging import configure_logging
from enterprise_rag.database.session import engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "application_starting",
        application=app.title,
        version=app.version,
    )

    yield

    await engine.dispose()

    logger.info("application_shutting_down")


def create_application() -> FastAPI:
    settings = get_settings()

    configure_logging(settings.log_level)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.include_router(
        health_router,
        prefix=settings.api_v1_prefix,
    )

    application.include_router(
        users_router,
        prefix=f"{settings.api_v1_prefix}/users",
    )

    return application
