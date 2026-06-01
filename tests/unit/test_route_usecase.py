from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from usecases.route_usecase import get_trip_plan


@pytest.mark.asyncio
@patch("usecases.route_usecase.fetch_route_from_otp")
async def test_route_exists(
    mock_fetch,
):

    mock_fetch.return_value = {
        "data": {
            "plan": {
                "itineraries": [
                    {"legs": []}
                ]
            }
        }
    }

    class MockRequest:
        from_lat = 0
        from_lon = 0
        to_lat = 1
        to_lon = 1

    result = await get_trip_plan(
        MockRequest()
    )

    assert len(result) == 1


@pytest.mark.asyncio
@patch("usecases.route_usecase.fetch_route_from_otp")
async def test_no_route_exists(
    mock_fetch,
):

    mock_fetch.return_value = {
        "data": {
            "plan": {
                "itineraries": []
            }
        }
    }

    class MockRequest:
        from_lat = 0
        from_lon = 0
        to_lat = 1
        to_lon = 1

    result = await get_trip_plan(
        MockRequest()
    )

    assert result == []


@pytest.mark.asyncio
@patch("usecases.route_usecase.fetch_route_from_otp")
async def test_otp_error(
    mock_fetch,
):

    mock_fetch.return_value = {
        "error": "OTP unavailable"
    }

    class MockRequest:
        from_lat = 0
        from_lon = 0
        to_lat = 1
        to_lon = 1

    with pytest.raises(
        HTTPException
    ) as exc:

        await get_trip_plan(
            MockRequest()
        )

    assert exc.value.status_code == 502


@pytest.mark.asyncio
@patch("usecases.route_usecase.fetch_route_from_otp")
async def test_missing_plan(
    mock_fetch,
):

    mock_fetch.return_value = {
        "data": {}
    }

    class MockRequest:
        from_lat = 0
        from_lon = 0
        to_lat = 1
        to_lon = 1

    with pytest.raises(
        HTTPException
    ) as exc:

        await get_trip_plan(
            MockRequest()
        )

    assert exc.value.status_code == 502