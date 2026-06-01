from usecases.route_transformer import transform_otp_itinerary


def test_single_bus_leg(mock_fare_config):

    itinerary = {
        "legs": [
            {
                "mode": "BUS",
                "distance": 5000,
                "from": {"name": "Saris"},
                "to": {"name": "Megenagna"},
                "legGeometry": {"points": "abc"},
            }
        ]
    }

    result = transform_otp_itinerary(
        itinerary,
        mock_fare_config,
    )

    assert result["taxi_count"] == 1
    assert result["transfers"] == 0
    assert result["totalTripDistance"] == 5.0


def test_multiple_bus_legs(mock_fare_config):

    itinerary = {
        "legs": [
            {
                "mode": "BUS",
                "distance": 3000,
                "from": {"name": "A"},
                "to": {"name": "B"},
                "legGeometry": {"points": "abc"},
            },
            {
                "mode": "BUS",
                "distance": 4000,
                "from": {"name": "B"},
                "to": {"name": "C"},
                "legGeometry": {"points": "abc"},
            },
            {
                "mode": "BUS",
                "distance": 5000,
                "from": {"name": "C"},
                "to": {"name": "D"},
                "legGeometry": {"points": "abc"},
            },
        ]
    }

    result = transform_otp_itinerary(
        itinerary,
        mock_fare_config,
    )

    assert result["taxi_count"] == 3
    assert result["transfers"] == 2


def test_walk_and_bus_route(mock_fare_config):

    itinerary = {
        "legs": [
            {
                "mode": "WALK",
                "distance": 1000,
                "from": {"name": "A"},
                "to": {"name": "B"},
                "legGeometry": {"points": "abc"},
            },
            {
                "mode": "BUS",
                "distance": 5000,
                "from": {"name": "B"},
                "to": {"name": "C"},
                "legGeometry": {"points": "abc"},
            },
        ]
    }

    result = transform_otp_itinerary(
        itinerary,
        mock_fare_config,
    )

    assert result["totalWalkDistance"] == 1.0
    assert result["taxi_count"] == 1


def test_empty_itinerary(mock_fare_config):

    itinerary = {
        "legs": []
    }

    result = transform_otp_itinerary(
        itinerary,
        mock_fare_config,
    )

    assert result["tripDetail"] == []