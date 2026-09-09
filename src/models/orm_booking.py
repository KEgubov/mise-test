from datetime import date, time
from typing import Annotated, Optional

from sqlalchemy import String, Time, Date, Enum, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from src.core.enums import BookingStatus

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_20 = Annotated[str, 20]


class Base(DeclarativeBase):
    """Базовый declarative-класс для всех ORM-моделей приложения."""

    type_annotation_map = {
        str_20: String(20),
    }

    def __repr__(self) -> str:
        """Краткое строковое представление модели со всеми колонками."""
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)!r}")
        return f"<{self.__class__.__name__}, {', '.join(cols)}>"


class BookingDetail(Base):
    __tablename__ = "booking_details"

    booking_id: Mapped[intpk]
    guest_name: Mapped[str_20]
    guest_phone: Mapped[str]

    # Дата - не раньше сегодня, не позднее +90 дней
    booking_date: Mapped[date] = mapped_column(Date)

    # Время - слоты 12:00, 13:00 ... 22:00
    booking_time: Mapped[time] = mapped_column(Time)
    guests: Mapped[int]

    # Статус брони, либо 'active' либо 'cancelled'
    status: Mapped[BookingStatus] = mapped_column(String(20))
