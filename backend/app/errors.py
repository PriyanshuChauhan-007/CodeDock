from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def validation_error_response(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return one stable error shape for malformed API requests."""

    del request
    details: list[dict[str, Any]] = []
    for error in exc.errors():
        details.append(
            {
                "location": list(error.get("loc", ())),
                "message": error.get("msg", "Invalid request"),
                "type": error.get("type", "validation_error"),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request could not be validated.",
                "details": details,
            }
        },
    )
