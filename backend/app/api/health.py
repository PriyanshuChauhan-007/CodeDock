from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import check_database_connection

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live() -> dict[str, str]:
    """Report whether the API process is alive."""

    return {"status": "ok"}


@router.get("/ready")
async def ready() -> JSONResponse:
    """Report readiness only when required database dependencies are available."""

    try:
        await check_database_connection()
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": {"application": "ok", "postgres": "unavailable"},
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "checks": {"application": "ok", "postgres": "ok"},
        },
    )
