from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live() -> dict[str, str]:
    """Report whether the API process is alive."""

    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, object]:
    """Report application readiness until external dependency checks are added."""

    return {
        "status": "ok",
        "checks": {
            "application": "ok",
        },
    }
