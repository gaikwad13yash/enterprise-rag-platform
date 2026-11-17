from fastapi import APIRouter, HTTPException, status

from enterprise_rag.core.config import get_settings
from enterprise_rag.database.health import check_database_connection
from enterprise_rag.database.session import engine

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict:
    settings = get_settings()

    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ready")
async def readiness_check() -> dict:
    database_connected = await check_database_connection(engine)

    if not database_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "database": "unavailable",
            },
        )

    return {
        "status": "ready",
        "database": "connected",
    }
