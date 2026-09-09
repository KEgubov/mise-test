from typing import AsyncGenerator, Any

from src.core.db_conn import async_session
from src.services.booking_service import BookingService
from fastapi import Request


def get_booking_service(request: Request) -> BookingService:
    return request.app.state.booking_service

async def get_session() -> AsyncGenerator[Any, Any]:
    async with async_session() as session:
        yield session