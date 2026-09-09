from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.dependency import get_booking_service, get_session
from src.schemas.booking_schemas import BookingAddDTO, BookingDTO, BookingListResponse
from src.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    response_model=BookingDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое бронирование",
    description="Создаёт бронь, если время свободно. Возвращает 409, если время занято.",
)
async def create_booking(
    booking: BookingAddDTO,
    booking_service: BookingService = Depends(get_booking_service),
    session: AsyncSession = Depends(get_session),
) -> BookingDTO | None:
    """Создать бронь. Возвращает 201 и объект брони."""
    return await booking_service.create_booking(session, booking)


@router.get(
    "/",
    response_model=BookingListResponse,
    summary="Получить список бронирований на дату",
    description="Возвращает все бронирования на указанную дату. Если броней нет — пустой список.",
)
async def get_bookings(
    booking_date: date,
    booking_service: BookingService = Depends(get_booking_service),
    session: AsyncSession = Depends(get_session),
) -> BookingListResponse | None:
    """Список броней на дату: ?booking_date=2026-08-20."""
    return await booking_service.get_bookings_list(session, booking_date)


@router.get(
    "/{booking_id}",
    response_model=BookingDTO,
    summary="Получить бронирование по ID",
    description="Возвращает 404, если бронирование не найдено.",
)
async def get_booking_by_id(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
    session: AsyncSession = Depends(get_session),
) -> BookingDTO:
    """Получить одну бронь по id."""
    booking = await booking_service.get_booking_by_id(session, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с id={booking_id} не найдено",
        )
    return booking


@router.patch(
    "/{booking_id}",
    response_model=BookingDTO,
    summary="Отменить бронирование",
    description="Меняет статус на CANCELED. Запись не удаляется физически.",
)
async def cancel_booking(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
    session: AsyncSession = Depends(get_session),
) -> BookingDTO | None:
    """Отменить бронь по id."""
    try:
        return await booking_service.cancel_booking(session, booking_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с id={booking_id} не найдено",
        )