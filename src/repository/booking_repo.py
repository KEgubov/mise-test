from datetime import date, time

from sqlalchemy import select, Row, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import BookingStatus
from src.models.orm_booking import BookingDetail
from src.services.exception import DuplicateError


class BookingRepository:
    """
    Репозиторий для работы с сущностью бронирования (BookingDetail) в базе данных.
    Инкапсулирует всю логику взаимодействия с таблицей booking_details.
    """

    @staticmethod
    async def find_booking_in_db(session: AsyncSession, booking_date: date, booking_time: time) -> BookingDetail | None:
        """
        Ищет существующую бронь в базе данных по заданной дате и времени.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_date: Дата бронирования.
            booking_time: Время бронирования.

        Returns:
            Объект BookingDetail, если бронь найдена, иначе None.
        """
        query = (
            select(BookingDetail)
            .where(
                BookingDetail.booking_date == booking_date,
                BookingDetail.booking_time == booking_time
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_booking_in_db(session: AsyncSession, booking: BookingDetail):
        """
        Добавляет новую запись о бронировании в базу данных.

        В случае нарушения уникальности (например, дублирование даты и времени),
        перехватывает IntegrityError и выбрасывает кастомное исключение DuplicateError.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking: Экземпляр модели BookingDetail для сохранения.

        Returns:
            Сохраненный объект BookingDetail с присвоенным ID.

        Raises:
            DuplicateError: Если бронь с такими параметрами уже существует в БД.
        """
        try:
            session.add(booking)
            await session.commit()
            await session.refresh(booking)
            return booking
        except IntegrityError as e:
            await session.rollback()
            if "already exists" in str(e.orig).lower():
                raise DuplicateError(
                    message="Booking already exists",
                    error_code="BOOKING_DUPLICATE",
                )

    @staticmethod
    async def get_bookings_list(session: AsyncSession, booking_date: date) -> list[BookingDetail]:
        """
        Получает список всех бронирований на конкретную дату.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_date: Дата, за которую нужно получить список бронирований.

        Returns:
            Список объектов BookingDetail, отсортированных по времени.
        """
        query = (
            select(BookingDetail)
            .where(BookingDetail.booking_date == booking_date)
            .order_by(BookingDetail.booking_time)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_booking_by_id(session: AsyncSession, booking_id: int) -> BookingDetail | None:
        """
        Ищет бронирование по его уникальному идентификатору.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_id: Уникальный идентификатор бронирования.

        Returns:
            Объект BookingDetail, если запись найдена, иначе None.
        """
        query = (
            select(BookingDetail)
            .where(BookingDetail.booking_id == booking_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def cancel_booking(session: AsyncSession, booking_id: int) -> BookingDetail:
        """
        Отменяет существующее бронирование, изменяя его статус на CANCELED.
        Использует оператор UPDATE с конструкцией RETURNING для получения обновленной записи.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            booking_id: Уникальный идентификатор бронирования для отмены.

        Returns:
            Обновленный объект BookingDetail со статусом CANCELED.
        """
        status = BookingStatus.CANCELED
        stmt = (
            update(BookingDetail)
            .where(BookingDetail.booking_id == booking_id)
            .values(status=status)
            .returning(BookingDetail)
        )
        result = await session.execute(stmt)
        booking = result.scalar_one()
        await session.commit()
        return booking
