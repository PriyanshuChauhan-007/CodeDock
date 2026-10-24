from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.router import api_router
from app.config import get_settings
from app.errors import validation_error_response


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Secure asynchronous code execution platform API.",
    )
    application.include_router(api_router)
    application.add_exception_handler(
        RequestValidationError, validation_error_response
    )
    return application


app = create_app()
