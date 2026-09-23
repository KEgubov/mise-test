from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from tests.confest import (
    mock_booking_dto,
    client,
    mock_booking_service,
    mock_session,
    mock_booking_add_dto,
    mock_booking_list,
)


@pytest.mark.asyncio
async def test_create_booking_returns_201(
    client, mock_booking_service, mock_session, mock_booking_add_dto, mock_booking_dto
):
    mock_booking_service.create_booking = AsyncMock(return_value=mock_booking_dto)

    async with client as c:
        response = await c.post("/bookings/", json=mock_booking_add_dto)

    assert response.status_code == 201
    assert response.json()["booking_id"] == mock_booking_dto.booking_id
    assert response.json()["status"] == mock_booking_dto.status


@pytest.mark.asyncio
async def test_get_bookings_by_id_success(
    client, mock_booking_service, mock_booking_dto
):
    mock_booking_service.get_booking_by_id = AsyncMock(return_value=mock_booking_dto)

    async with client as c:
        response = await c.get("/bookings/1")

    assert response.status_code == 200
    assert response.json()["booking_id"] == 1


@pytest.mark.asyncio
async def test_get_booking_by_id_not_found_returns_404(
    client, mock_booking_service, mock_session
):
    mock_booking_service.get_booking_by_id = AsyncMock(
        side_effect=HTTPException(status_code=404, detail="Booking not found")
    )

    async with client as c:
        response = await c.get("/bookings/2")

    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


@pytest.mark.asyncio
async def test_cancel_booking_success_returns_200(
    client, mock_booking_service, mock_session, mock_booking_dto
):
    mock_booking_dto.status = "cancelled"
    mock_booking_service.cancel_booking = AsyncMock(return_value=mock_booking_dto)

    async with client as c:
        response = await c.patch("/bookings/1")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_booking_not_found_returns_404(
        client, mock_booking_service, mock_session, mock_booking_dto
):
    mock_booking_service.cancel_booking = AsyncMock(
        side_effect=HTTPException(status_code=404, detail="Booking not found")
    )
    async with client as c:
        response = await c.patch("/bookings/2")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Бронирование с id={2} не найдено"


@pytest.mark.asyncio
async def test_get_bookings_success_returns_200(
        client, mock_booking_service, mock_session, mock_booking_list
):
    mock_booking_service.get_bookings_list = AsyncMock(return_value=mock_booking_list)

    async with client as c:
        response = await c.get("/bookings/", params={"booking_date": str(date.today() + timedelta(days=1))})

    assert response.status_code == 200
    assert len(response.json()["bookings"]) == 1
