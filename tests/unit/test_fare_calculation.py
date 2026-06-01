from usecases.route_transformer import calculate_cost


def test_zero_distance_returns_zero(mock_fare_config):
    result = calculate_cost(0, mock_fare_config)

    assert result == 0


def test_base_fare(mock_fare_config):
    result = calculate_cost(2.5, mock_fare_config)

    assert result == 10


def test_additional_distance_charge(mock_fare_config):
    result = calculate_cost(5.0, mock_fare_config)

    assert result == 15


def test_long_distance_charge(mock_fare_config):
    result = calculate_cost(10.0, mock_fare_config)

    assert result > 15