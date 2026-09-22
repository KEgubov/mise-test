from datetime import date, time
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from src.api.dependency import get_booking_service, get_session
from src.schemas.booking_schemas import BookingDTO


@pytest.fixture
def mock_booking_service():
    return MagicMock()

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_booking():
    return BookingDTO(
        booking_id=1,
        status="active",
        guest_name="John",
        guest_phone="+79999999999",
        booking_date=date(2026, 9, 22),
        booking_time=time(14, 00),
        guests=1
    )

@pytest.fixture
def client(mock_booking_service, mock_session):

    app.dependency_overrides[get_booking_service] = lambda: mock_booking_service
    app.dependency_overrides[get_session] = lambda: mock_session

    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    app.dependency_overrides.clear()