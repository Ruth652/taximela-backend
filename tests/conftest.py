from types import SimpleNamespace
import pytest


@pytest.fixture
def mock_fare_config():
    return SimpleNamespace(
        base_fare_etb=10,
        base_distance_km=2.5,
        step_distance_km=2.5,
        step_fare_etb=5,
    )