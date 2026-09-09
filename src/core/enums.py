import enum


class BookingStatus(enum.StrEnum):
    ACTIVE = "active"
    CANCELED = "cancelled"
