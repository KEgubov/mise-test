from fastapi import Request, Response
from starlette.responses import JSONResponse

from src.services.exception import DuplicateError, BookingTimeAlreadyTakenError


def duplicate_error_handler(request: Request, exc: DuplicateError) -> Response:
    """Обрабатывает DuplicateError: отвечает HTTP 409 с кодом и сообщением."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
        },
    )


def booking_time_error_handler(request: Request, exc: BookingTimeAlreadyTakenError) -> Response:
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
        }
    )