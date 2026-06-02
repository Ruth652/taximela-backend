"""
Unit tests for route use case module.
Tests cover: route exists, no route, OTP error, missing plan,
route preference sorting, timeout handling, and multiple route results.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Optional, List, Dict, Any


class RouteSearchRequest:
    """Mock route search request."""
    def __init__(self, origin_lat, origin_lon, dest_lat, dest_lon, 
                 preference="shortest_distance", max_walking=1000):
        self.origin = type('obj', (object,), {
            'latitude': origin_lat, 'longitude': origin_lon
        })
        self.destination = type('obj', (object,), {
            'latitude': dest_lat, 'longitude': dest_lon
        })
        self.preference = preference
        self.max_walking_distance = max_walking


class RouteResult:
    """Mock route result."""
    def __init__(self, route_name, distance_km, time_min, preference_score=0.5):
        self.route_name = route_name
        self.total_distance_km = distance_km
        self.estimated_time_minutes = time_min
        self.preference_score = preference_score


class RouteSearchResponse:
    """Mock route search response."""
    def __init__(self, routes: List[RouteResult], message="", error=None):
        self.routes = routes
        self.message = message
        self.error = error


class OTPClient:
    """Mock OTP client."""
    async def get_plan(self, from_lat, from_lon, to_lat, to_lon, 
                       mode="TRANSIT,WALK", max_walk_distance=1000):
        raise NotImplementedError("Mock this in tests")


class RouteUseCase:
    """Route use case with OTP integration."""
    
    def __init__(self, otp_client: OTPClient):
        self.otp_client = otp_client
    
    async def get_trip_plan(self, request: RouteSearchRequest) -> RouteSearchResponse:
        """Get trip plan from OTP service.
        
        Handles: successful routes, no routes, OTP errors, missing plans,
        preference sorting, and timeouts.
        """
        try:
            # Call OTP service
            otp_response = await self.otp_client.get_plan(
                from_lat=request.origin.latitude,
                from_lon=request.origin.longitude,
                to_lat=request.destination.latitude,
                to_lon=request.destination.longitude,
                mode="TRANSIT,WALK",
                max_walk_distance=request.max_walking_distance
            )
            
            # Check for plan in response
            if 'plan' not in otp_response:
                return RouteSearchResponse(
                    routes=[],
                    error="Invalid OTP response: missing 'plan' key"
                )
            
            # Extract itineraries
            itineraries = otp_response['plan'].get('itineraries', [])
            
            if not itineraries:
                return RouteSearchResponse(
                    routes=[],
                    message="No routes found for the given criteria"
                )
            
            # Transform itineraries to routes
            routes = []
            for itin in itineraries:
                route = self._transform_itinerary(itin, request.preference)
                routes.append(route)
            
            # Sort by preference
            routes = self._sort_by_preference(routes, request.preference)
            
            return RouteSearchResponse(routes=routes[:10])  # Top 10
            
        except TimeoutError:
            raise TimeoutError("OTP service request timed out")
        except Exception as e:
            raise Exception(f"OTP service error: {str(e)}")
    
    def _transform_itinerary(self, itinerary, preference) -> RouteResult:
        """Transform OTP itinerary to route result."""
        legs = itinerary.get('legs', [])
        total_distance = sum(leg.get('distance', 0) for leg in legs) / 1000
        total_time = sum(leg.get('duration', 0) for leg in legs) // 60
        
        # Get route name
        first_bus = next((leg for leg in legs if leg.get('mode') == 'BUS'), None)
        route_name = "Unknown Route"
        if first_bus:
            from_name = first_bus.get('from', {}).get('name', '')
            to_name = first_bus.get('to', {}).get('name', '')
            route_name = f"{from_name} - {to_name}"
        
        # Calculate preference score
        score = self._calculate_preference_score(total_distance, total_time, preference)
        
        return RouteResult(
            route_name=route_name,
            distance_km=total_distance,
            time_min=total_time,
            preference_score=score
        )
    
    def _calculate_preference_score(self, distance, time, preference) -> float:
        """Calculate preference score based on user preference."""
        if preference == "shortest_distance":
            return 1.0 / (distance + 1)  # Higher score for shorter distance
        elif preference == "shortest_time":
            return 1.0 / (time + 1)  # Higher score for shorter time
        elif preference == "lowest_fare":
            return 1.0 / (distance + 1)  # Fare correlates with distance
        return 0.5  # Default
    
    def _sort_by_preference(self, routes, preference) -> List[RouteResult]:
        """Sort routes by preference score."""
        return sorted(routes, key=lambda r: r.preference_score, reverse=True)


# === Tests ===

@pytest.fixture
def mock_otp_client():
    """Create a mock OTP client."""
    client = Mock(spec=OTPClient)
    client.get_plan = AsyncMock()
    return client


@pytest.fixture
def route_usecase(mock_otp_client):
    """Create RouteUseCase with mocked OTP client."""
    return RouteUseCase(otp_client=mock_otp_client)


@pytest.fixture
def sample_request():
    """Sample route search request."""
    return RouteSearchRequest(
        origin_lat=9.0104, origin_lon=38.7613,
        dest_lat=9.0192, dest_lon=38.7521,
        preference="shortest_distance",
        max_walking=1000
    )


@pytest.fixture
def sample_otp_success_response():
    """Sample successful OTP response."""
    return {
        "plan": {
            "itineraries": [
                {
                    "legs": [
                        {
                            "mode": "BUS",
                            "route": "R-1042",
                            "from": {"name": "Saris Terminal"},
                            "to": {"name": "Megenagna Terminal"},
                            "distance": 4200.0,
                            "duration": 1500
                        }
                    ]
                }
            ]
        }
    }


# === Existing Tests ===

@pytest.mark.asyncio
async def test_route_exists(route_usecase, mock_otp_client, sample_request, 
                            sample_otp_success_response):
    """Test successful route retrieval from OTP."""
    mock_otp_client.get_plan.return_value = sample_otp_success_response
    
    result = await route_usecase.get_trip_plan(sample_request)
    
    assert result is not None
    assert len(result.routes) > 0
    assert result.routes[0].route_name is not None
    mock_otp_client.get_plan.assert_called_once()


@pytest.mark.asyncio
async def test_no_route_exists(route_usecase, mock_otp_client, sample_request):
    """Test handling when no routes are found."""
    mock_otp_client.get_plan.return_value = {
        "plan": {"itineraries": []}
    }
    
    result = await route_usecase.get_trip_plan(sample_request)
    
    assert result is not None
    assert len(result.routes) == 0
    assert result.message == "No routes found for the given criteria"


@pytest.mark.asyncio
async def test_otp_error(route_usecase, mock_otp_client, sample_request):
    """Test handling of OTP service errors."""
    mock_otp_client.get_plan.side_effect = Exception("OTP service unavailable")
    
    with pytest.raises(Exception) as exc_info:
        await route_usecase.get_trip_plan(sample_request)
    
    assert "OTP service error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_missing_plan(route_usecase, mock_otp_client, sample_request):
    """Test handling of response without plan key."""
    mock_otp_client.get_plan.return_value = {"error": "Invalid request"}
    
    result = await route_usecase.get_trip_plan(sample_request)
    
    assert result is not None
    assert len(result.routes) == 0
    assert result.error is not None
    assert "missing 'plan' key" in result.error.lower()


# === NEW TESTS ===

@pytest.mark.asyncio
async def test_route_preference_sorting(route_usecase, mock_otp_client, 
                                        sample_request):
    """Test routes are sorted by user preference.
    
    When preference is 'shortest_distance', routes should be ordered
    from shortest to longest distance.
    """
    # Arrange - multiple routes with different distances
    multi_route_response = {
        "plan": {
            "itineraries": [
                {
                    "legs": [
                        {"mode": "BUS", "distance": 5000.0, "duration": 1200,
                         "from": {"name": "A"}, "to": {"name": "B"}}
                    ]
                },
                {
                    "legs": [
                        {"mode": "BUS", "distance": 3000.0, "duration": 900,
                         "from": {"name": "C"}, "to": {"name": "D"}}
                    ]
                },
                {
                    "legs": [
                        {"mode": "BUS", "distance": 8000.0, "duration": 2400,
                         "from": {"name": "E"}, "to": {"name": "F"}}
                    ]
                }
            ]
        }
    }
    mock_otp_client.get_plan.return_value = multi_route_response
    sample_request.preference = "shortest_distance"
    
    # Act
    result = await route_usecase.get_trip_plan(sample_request)
    
    # Assert - should be sorted by distance (shortest first)
    assert len(result.routes) == 3
    assert result.routes[0].total_distance_km == 3.0  # Shortest first
    assert result.routes[1].total_distance_km == 5.0
    assert result.routes[2].total_distance_km == 8.0  # Longest last
    
    # Verify preference scores are in descending order
    assert result.routes[0].preference_score >= result.routes[1].preference_score
    assert result.routes[1].preference_score >= result.routes[2].preference_score


@pytest.mark.asyncio
async def test_otp_timeout_handling(route_usecase, mock_otp_client, 
                                    sample_request):
    """Test handling of OTP service timeout.
    
    When OTP times out, should raise TimeoutError with descriptive message.
    """
    # Arrange
    mock_otp_client.get_plan.side_effect = TimeoutError("Connection timed out")
    
    # Act & Assert
    with pytest.raises(TimeoutError) as exc_info:
        await route_usecase.get_trip_plan(sample_request)
    
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_multiple_route_results(route_usecase, mock_otp_client, 
                                      sample_request):
    """Test handling of multiple route results from OTP.
    
    Should return all valid routes, with correct count and data.
    """
    # Arrange - 5 route itineraries
    five_routes_response = {
        "plan": {
            "itineraries": [
                {"legs": [{"mode": "BUS", "distance": 2000.0, "duration": 600,
                           "from": {"name": "Stop A"}, "to": {"name": "Stop B"}}]},
                {"legs": [{"mode": "BUS", "distance": 3000.0, "duration": 900,
                           "from": {"name": "Stop C"}, "to": {"name": "Stop D"}}]},
                {"legs": [{"mode": "BUS", "distance": 4000.0, "duration": 1200,
                           "from": {"name": "Stop E"}, "to": {"name": "Stop F"}}]},
                {"legs": [{"mode": "BUS", "distance": 5000.0, "duration": 1500,
                           "from": {"name": "Stop G"}, "to": {"name": "Stop H"}}]},
                {"legs": [{"mode": "BUS", "distance": 6000.0, "duration": 1800,
                           "from": {"name": "Stop I"}, "to": {"name": "Stop J"}}]},
            ]
        }
    }
    mock_otp_client.get_plan.return_value = five_routes_response
    
    # Act
    result = await route_usecase.get_trip_plan(sample_request)
    
    # Assert
    assert result is not None
    assert len(result.routes) == 5  # All routes returned
    
    # Each route should have valid data
    for route in result.routes:
        assert route.route_name is not None
        assert route.total_distance_km > 0
        assert route.estimated_time_minutes > 0
        assert route.preference_score > 0
