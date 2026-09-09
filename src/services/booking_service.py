from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date
from src.core.enums import BookingStatus
from src.models.orm_booking import BookingDetail
from src.repository.booking_repo import BookingRepository
from src.schemas.booking_schemas import BookingAddDTO, BookingDTO, BookingListResponse
from src.services.exception import BookingTimeAlreadyTakenError


class BookingService:
    """
    Сервисный слой для бизнес-логики, связанной с бронированиями.
    Координирует работу между репозиторием, DTO и обработкой исключений.
    """
    def __init__(self, booking_repository: BookingRepository):
        self.booking_repository = booking_repository

    async def create_booking(self, session: AsyncSession, booking: BookingAddDTO) -> BookingDTO | None:
        """
        Создаёт новое бронирование, если указанное время свободно.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking: DTO с данными для создания бронирования.

        Returns:
            BookingDTO: Данные созданного бронирования.

        Raises:
            BookingTimeAlreadyTakenError: Если на указанную дату и время уже есть бронь.
        """
        find_booking = await self.booking_repository.find_booking_in_db(session, booking.booking_date,
                                                                        booking.booking_time)
        if find_booking is not None:
            raise BookingTimeAlreadyTakenError(
                message=f"Время {booking.booking_date} {booking.booking_time} уже занято",
            )

        model_booking = BookingDetail(
            guest_name=booking.guest_name,
            guest_phone=booking.guest_phone,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            guests=booking.guests,
            status=BookingStatus.ACTIVE,
        )
        added_booking = await self.booking_repository.create_booking_in_db(session, model_booking)
        if added_booking:
            result_dto = BookingDTO.model_validate(added_booking, from_attributes=True)
            return result_dto

    async def get_bookings_list(self, session: AsyncSession, booking_date: date) -> BookingListResponse:
        """
        Получает список всех бронирований на указанную дату.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_date: Дата, за которую запрашиваются бронирования.

        Returns:
            BookingListResponse: Объект, содержащий список DTO бронирований.
            Если бронирований нет, возвращает объект с пустым списком.
        """
        all_bookings = await self.booking_repository.get_bookings_list(session, booking_date)
        bookings_dto = [
            BookingDTO.model_validate(booking, from_attributes=True)
            for booking in all_bookings
        ]
        return BookingListResponse(bookings=bookings_dto)


    async def get_booking_by_id(self, session: AsyncSession, booking_id: int) -> BookingDTO | None:
        """
        Получает данные конкретного бронирования по его ID.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_id: Уникальный идентификатор бронирования.

        Returns:
            BookingDTO, если бронирование найдено, иначе None.
        """
        booking = await self.booking_repository.get_booking_by_id(session, booking_id)
        if booking:
            result_dto = BookingDTO.model_validate(booking, from_attributes=True)
            return result_dto
        return None

    async def cancel_booking(self, session: AsyncSession, booking_id: int) -> BookingDTO | None:
        """
        Отменяет существующее бронирование по его ID.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_id: Уникальный идентификатор бронирования для отмены.

        Returns:
            BookingDTO: Данные обновленного бронирования со статусом CANCELED.
        """
        modified_booking = await self.booking_repository.cancel_booking(session, booking_id)
        if modified_booking:
            result_dto = BookingDTO.model_validate(modified_booking, from_attributes=True)
            return result_dto
        return None

