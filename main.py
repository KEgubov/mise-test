from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import main_router
from src.api.exception_handler import duplicate_error_handler, booking_time_error_handler
from src.repository.booking_repo import BookingRepository
from src.services.booking_service import BookingService
from src.services.exception import DuplicateError, BookingTimeAlreadyTakenError

async def init_services(app: FastAPI):
    """Инициализация бизнес-сервисов"""
    app.state.booking_service = BookingService(booking_repository=BookingRepository())

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: инициализация зависимостей при старте."""
    await init_services(app)
    yield

app = FastAPI(title="MISA Test", lifespan=lifespan)

app.include_router(main_router)

app.add_exception_handler(DuplicateError, duplicate_error_handler)
app.add_exception_handler(BookingTimeAlreadyTakenError, booking_time_error_handler)
