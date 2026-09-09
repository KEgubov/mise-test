from datetime import date, time, timedelta

import phonenumbers
from pydantic import BaseModel, Field, field_validator


class BookingAddDTO(BaseModel):
    """Модель Pydantic для входящих данных бронирования"""

    guest_name: str = Field(min_length=2, description="Имя гостя", examples=["Кирилл"])
    guest_phone: str = Field(..., description="Номер телефона гостя", examples=["+79997776615"])
    booking_date: date = Field(..., description="Дата бронирования", examples=[date(year=2026, month=9, day=10)])
    booking_time: time = Field(..., description="Время бронирования", examples=[time(hour=10, minute=0)])
    guests: int = Field(ge=1, le=12, description="Количество гостей", examples=[4])

    @field_validator("guest_phone")
    @classmethod
    def guest_phone_validator(cls, v):
        try:
            # Если нет плюса, считаем, что это Россия (пользователи ленятся ставить +)
            parsed = phonenumbers.parse(v, "RU")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Номер не существует")

            # Строгая проверка, что это именно МОБИЛЬНЫЙ номер
            # (отсеет городские, бесплатные 8-800 и сервисные номера)
            if phonenumbers.number_type(parsed) != phonenumbers.PhoneNumberType.MOBILE:
                raise ValueError("Разрешены только мобильные номера")

            # Нормализуем в E.164
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Некорректный формат номера")

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, v):
        today = date.today()
        max_date = today + timedelta(days=90)

        if v < today:
            raise ValueError("Дата бронирования не может быть раньше сегодня")
        if v > max_date:
            raise ValueError(
                "Дата бронирования не может быть позднее чем через 90 дней"
            )
        return v

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, v):
        # Только часы: 12:00, 13:00 ... 22:00 с шагом 1 час
        if v.hour < 12 or v.hour > 22 or v.minute != 0:
            raise ValueError("Доступные слоты: 12:00, 13:00, ..., 22:00")
        return v


class BookingDTO(BookingAddDTO):
    booking_id: int = Field(..., description="ID брони")
    status: str = Field(..., description="Статус брони", examples=["active", "cancelled"])


class BookingListResponse(BaseModel):
    """Обёртка списка бронирований."""

    bookings: list[BookingDTO]
