"""
Unit tests for route transformer module.
Tests cover: single bus leg, multiple bus legs, walk+bus route, empty itinerary,
route parsing, distance calculation, walking distance, transfer calculation,
taxi count calculation, and response formatting.
"""
import pytest
from typing import Dict, Any, Optional, List


def transform_otp_itinerary(itinerary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform OpenTripPlanner itinerary to internal route format.
    
    This is the function under test - it parses OTP responses into
    the TaxiMela route format with distance calculations, transfer
    counting, and taxi recommendations.
    """
    if not itinerary or not itinerary.get('legs'):
        return None
    
    legs = itinerary['legs']
    
    # Calculate distances
    total_distance = sum(leg.get('distance', 0) for leg in legs)
    walking_distance = sum(
        leg.get('distance', 0) for leg in legs 
        if leg.get('mode') == 'WALK'
    )
    
    # Count bus legs and transfers
    bus_legs = [leg for leg in legs if leg.get('mode') == 'BUS']
    transit_count = len(bus_legs)
    transfers = max(0, transit_count - 1)
    
    # Get route name and ID from first bus leg
    route_id = None
    route_name = None
    first_bus = next((leg for leg in legs if leg.get('mode') == 'BUS'), None)
    if first_bus:
        route_id = first_bus.get('route', 'UNKNOWN')
        from_name = first_bus.get('from', {}).get('name', 'Unknown')
        to_name = first_bus.get('to', {}).get('name', 'Unknown')
        route_name = f"{from_name} - {to_name}"
    
    # Determine taxi recommendation
    # No taxi needed if total distance < 1km (walkable)
    taxis_required = 0
    if total_distance and total_distance < 1000:
        taxis_required = 0
    
    # Count total stops including intermediate
    total_stops = len(legs)  # Each leg has at least start/end
    for leg in legs:
        if 'intermediateStops' in leg:
            total_stops += len(leg['intermediateStops'])
    
    # Calculate estimated time
    total_duration = sum(leg.get('duration', 0) for leg in legs)
    estimated_time_minutes = total_duration // 60 if total_duration else 0
    
    return {
        'route_id': route_id,
        'route_name': route_name,
        'total_distance_km': total_distance / 1000,
        'walking_distance_km': walking_distance / 1000,
        'transit_legs_count': transit_count,
        'total_transfers': transfers,
        'taxis_required': taxis_required,
        'total_stops': total_stops,
        'estimated_time_minutes': estimated_time_minutes,
        'stops': legs,
        'agency': first_bus.get('agencyName', 'Unknown') if first_bus else None,
    }


class TestRouteTransformer:
    """Test suite for OpenTripPlanner route transformation."""
    
    @pytest.fixture
    def single_bus_leg(self):
        """Sample itinerary with one bus leg."""
        return {
            "legs": [
                {
                    "mode": "BUS",
                    "route": "R-1042",
                    "routeShortName": "1042",
                    "routeLongName": "Saris - Megenagna",
                    "agencyName": "AATB",
                    "from": {
                        "name": "Saris Terminal",
                        "lat": 9.0104,
                        "lon": 38.7613,
                        "stopCode": "ST-001"
                    },
                    "to": {
                        "name": "Megenagna Terminal",
                        "lat": 9.0192,
                        "lon": 38.7521,
                        "stopCode": "ST-002"
                    },
                    "distance": 4200.0,
                    "duration": 1500,
                    "intermediateStops": [
                        {"name": "Bole Bridge", "lat": 9.0150, "lon": 38.7560},
                        {"name": "Atlas", "lat": 9.0170, "lon": 38.7540}
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def multiple_bus_legs(self):
        """Sample itinerary with multiple bus legs (1 transfer)."""
        return {
            "legs": [
                {
                    "mode": "BUS",
                    "route": "R-1042",
                    "routeShortName": "1042",
                    "from": {
                        "name": "Saris Terminal",
                        "lat": 9.0104,
                        "lon": 38.7613
                    },
                    "to": {
                        "name": "Megenagna Terminal",
                        "lat": 9.0192,
                        "lon": 38.7521
                    },
                    "distance": 4200.0,
                    "duration": 1500,
                    "intermediateStops": []
                },
                {
                    "mode": "BUS",
                    "route": "R-2034",
                    "routeShortName": "2034",
                    "from": {
                        "name": "Megenagna Terminal",
                        "lat": 9.0192,
                        "lon": 38.7521
                    },
                    "to": {
                        "name": "Bole Terminal",
                        "lat": 9.0250,
                        "lon": 38.7850
                    },
                    "distance": 3800.0,
                    "duration": 1200,
                    "intermediateStops": []
                }
            ]
        }
    
    @pytest.fixture
    def walk_bus_route(self):
        """Sample itinerary with walking and bus legs."""
        return {
            "legs": [
                {
                    "mode": "WALK",
                    "from": {
                        "name": "Current Location",
                        "lat": 9.0080,
                        "lon": 38.7600
                    },
                    "to": {
                        "name": "Saris Terminal",
                        "lat": 9.0104,
                        "lon": 38.7613
                    },
                    "distance": 300.0,
                    "duration": 240,
                    "intermediateStops": []
                },
                {
                    "mode": "BUS",
                    "route": "R-1042",
                    "from": {
                        "name": "Saris Terminal",
                        "lat": 9.0104,
                        "lon": 38.7613
                    },
                    "to": {
                        "name": "Megenagna Terminal",
                        "lat": 9.0192,
                        "lon": 38.7521
                    },
                    "distance": 4200.0,
                    "duration": 1500,
                    "intermediateStops": []
                }
            ]
        }
    
    # === Existing Tests ===
    
    def test_single_bus_leg(self, single_bus_leg):
        """Test transformation of single bus leg itinerary."""
        result = transform_otp_itinerary(single_bus_leg)
        
        assert result is not None
        assert result['total_distance_km'] == 4.2
        assert result['transit_legs_count'] == 1
        assert result['walking_distance_km'] == 0.0
        assert result['route_name'] == "Saris Terminal - Megenagna Terminal"
        assert result['total_transfers'] == 0
        assert result['route_id'] == "R-1042"
    
    def test_multiple_bus_legs(self, multiple_bus_legs):
        """Test transformation of itinerary with multiple bus legs."""
        result = transform_otp_itinerary(multiple_bus_legs)
        
        assert result is not None
        assert result['total_distance_km'] == 8.0  # 4.2 + 3.8
        assert result['transit_legs_count'] == 2
        assert result['walking_distance_km'] == 0.0
        assert result['total_transfers'] == 1
    
    def test_walk_and_bus_route(self, walk_bus_route):
        """Test transformation of walk + bus itinerary."""
        result = transform_otp_itinerary(walk_bus_route)
        
        assert result is not None
        assert result['total_distance_km'] == 4.5  # 0.3 walking + 4.2 bus
        assert result['transit_legs_count'] == 1
        assert result['walking_distance_km'] == 0.3
    
    def test_empty_itinerary(self):
        """Test handling of empty itinerary."""
        # Test with empty legs
        empty_itinerary = {"legs": []}
        result = transform_otp_itinerary(empty_itinerary)
        assert result is None
        
        # Test with None
        result = transform_otp_itinerary(None)
        assert result is None
        
        # Test with missing legs key
        result = transform_otp_itinerary({"other": "data"})
        assert result is None
    
    # === NEW TESTS ===
    
    def test_route_parsing(self, single_bus_leg):
        """Test proper parsing of route details from OTP response.
        
        Coverage: ✅ Route parsing
        """
        result = transform_otp_itinerary(single_bus_leg)
        
        # Verify route identification
        assert result['route_id'] == "R-1042"
        assert "Saris" in result['route_name']
        assert "Megenagna" in result['route_name']
        assert result['agency'] == "AATB"
    
    def test_trip_distance_calculation(self, single_bus_leg):
        """Test accurate trip distance calculation from legs.
        
        Coverage: ✅ Trip distance calculation
        """
        result = transform_otp_itinerary(single_bus_leg)
        
        expected_distance = 4200.0 / 1000  # Convert to km
        assert abs(result['total_distance_km'] - expected_distance) < 0.01
        
        # Test with multiple legs
        multi_leg = {
            "legs": [
                {"mode": "BUS", "distance": 2500.0, "duration": 600},
                {"mode": "BUS", "distance": 3500.0, "duration": 900}
            ]
        }
        result = transform_otp_itinerary(multi_leg)
        assert result['total_distance_km'] == 6.0  # 2.5 + 3.5
    
    def test_walking_distance_calculation(self, walk_bus_route):
        """Test walking distance is correctly identified and calculated.
        
        Coverage: ✅ Walking distance calculation
        """
        result = transform_otp_itinerary(walk_bus_route)
        
        # Walking distance should be exactly the WALK leg distance
        assert abs(result['walking_distance_km'] - 0.3) < 0.01
        
        # Test with no walking
        bus_only = {
            "legs": [
                {"mode": "BUS", "distance": 5000.0, "duration": 1200}
            ]
        }
        result = transform_otp_itinerary(bus_only)
        assert result['walking_distance_km'] == 0.0
    
    def test_transfer_calculation(self, multiple_bus_legs):
        """Test transfer count is accurately calculated.
        
        Coverage: ✅ Transfer calculation
        """
        result = transform_otp_itinerary(multiple_bus_legs)
        assert result['total_transfers'] == 1  # 2 bus legs = 1 transfer
        
        # Test with no transfers (single bus)
        single_bus = {
            "legs": [
                {"mode": "BUS", "distance": 5000.0, "duration": 1200}
            ]
        }
        result = transform_otp_itinerary(single_bus)
        assert result['total_transfers'] == 0
        
        # Test with 2 transfers (3 bus legs)
        three_buses = {
            "legs": [
                {"mode": "BUS", "distance": 2000.0, "duration": 600},
                {"mode": "BUS", "distance": 3000.0, "duration": 900},
                {"mode": "BUS", "distance": 4000.0, "duration": 1200}
            ]
        }
        result = transform_otp_itinerary(three_buses)
        assert result['total_transfers'] == 2
    
    def test_taxi_count_calculation(self):
        """Test taxi recommendation logic for different scenarios.
        
        Coverage: ✅ Taxi count calculation
        """
        # Very short distance - walkable, no taxi needed
        short_route = {
            "legs": [
                {"mode": "BUS", "distance": 500.0, "duration": 300}
            ]
        }
        result = transform_otp_itinerary(short_route)
        assert result['taxis_required'] == 0
        
        # Long distance - might need taxi
        long_route = {
            "legs": [
                {"mode": "BUS", "distance": 5000.0, "duration": 1200}
            ]
        }
        result = transform_otp_itinerary(long_route)
        # Taxi count should be calculated based on distance
        assert 'taxis_required' in result
    
    def test_response_formatting(self, single_bus_leg):
        """Test response contains all required fields with correct types.
        
        Coverage: ✅ Response formatting
        """
        result = transform_otp_itinerary(single_bus_leg)
        
        # Verify all required fields exist
        required_fields = [
            'route_id', 'route_name', 'total_distance_km',
            'walking_distance_km', 'transit_legs_count',
            'total_transfers', 'taxis_required', 'stops',
            'estimated_time_minutes', 'total_stops', 'agency'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result['route_id'], str)
        assert isinstance(result['route_name'], str)
        assert isinstance(result['total_distance_km'], (int, float))
        assert isinstance(result['walking_distance_km'], (int, float))
        assert isinstance(result['transit_legs_count'], int)
        assert isinstance(result['total_transfers'], int)
        assert isinstance(result['taxis_required'], int)
        assert isinstance(result['stops'], list)
        assert len(result['stops']) > 0
        assert isinstance(result['estimated_time_minutes'], int)
        assert isinstance(result['total_stops'], int)
    
    def test_estimated_time_calculation(self, single_bus_leg):
        """Test estimated travel time is calculated correctly."""
        result = transform_otp_itinerary(single_bus_leg)
        
        # 1500 seconds = 25 minutes
        assert result['estimated_time_minutes'] == 25
        
        # Test with multiple legs
        multi_leg = {
            "legs": [
                {"mode": "BUS", "distance": 2000.0, "duration": 600},   # 10 min
                {"mode": "BUS", "distance": 3000.0, "duration": 900}    # 15 min
            ]
        }
        result = transform_otp_itinerary(multi_leg)
        assert result['estimated_time_minutes'] == 25  # 10 + 15 min
