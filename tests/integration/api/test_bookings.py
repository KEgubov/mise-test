from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from tests.confest import mock_booking, client, mock_booking_service, mock_session


@pytest.mark.asyncio
async def test_get_bookings_by_id_success(client, mock_booking_service, mock_booking):
    mock_booking_service.get_booking_by_id = AsyncMock(return_value=mock_booking)

    async with client as c:
        response = await c.get("/bookings/1")

    assert response.status_code == 200
    assert response.json()["booking_id"] == 1

@pytest.mark.asyncio
async def test_get_booking_by_id_not_found_returns_404(client, mock_booking_service, mock_session):
    mock_booking_service.get_booking_by_id = AsyncMock(
        side_effect=HTTPException(status_code=404, detail="Booking not found")
    )

    async with client as c:
        response = await c.get("/bookings/2")

    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"

