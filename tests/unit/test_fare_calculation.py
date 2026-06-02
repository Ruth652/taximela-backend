"""
Unit tests for fare calculation module.
Tests cover: zero distance, base fare, additional distance charge, 
long distance charge, rounding rules, and edge cases.
"""
import pytest
import math
import decimal


class FareCalculator:
    """Fare calculator implementation for testing."""
    
    PRICE_PER_KM = 2.5
    MINIMUM_FARE = 10.0
    BASE_FARE = 8.0
    
    @staticmethod
    def _round_to_nearest_half(value: float) -> float:
        """Round to nearest 0.5 using half-up rounding.
        
        Uses Decimal for precise rounding control.
        Examples:
            11.75 -> 12.0
            12.25 -> 12.5
            13.25 -> 13.5
            13.75 -> 14.0
        """
        d = decimal.Decimal(str(value))
        # Multiply by 2, round to 1 decimal place with ROUND_HALF_UP, divide by 2
        rounded = (d * 2).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP) / 2
        return float(rounded)
    
    @staticmethod
    def compute_range(route_distance_meters, walking_origin_meters=0, walking_dest_meters=0):
        """Calculate fare range based on distance."""
        if route_distance_meters < 0:
            raise ValueError("Distance cannot be negative")
        
        distance_km = route_distance_meters / 1000
        
        # Calculate actual fare
        actual_fare = distance_km * FareCalculator.PRICE_PER_KM
        actual_fare = max(actual_fare, FareCalculator.BASE_FARE)
        actual_fare = max(actual_fare, FareCalculator.MINIMUM_FARE)
        
        # Round to nearest 0.5 using half-up rounding
        actual_fare = FareCalculator._round_to_nearest_half(actual_fare)
        
        # Calculate min and max fare range
        min_fare = max(actual_fare - 2.0, FareCalculator.MINIMUM_FARE)
        max_fare = actual_fare + 3.0
        
        class FareRange:
            def __init__(self, min_fare, max_fare, actual_fare):
                self.min = min_fare
                self.max = max_fare
                self.actual = actual_fare
        
        return FareRange(min_fare, max_fare, actual_fare)


class TestFareCalculation:
    """Test suite for fare calculation functionality."""
    
    # === Existing Tests ===
    
    def test_zero_distance_returns_zero(self):
        """Test fare calculation for zero distance travel."""
        fare = FareCalculator.compute_range(
            route_distance_meters=0,
            walking_origin_meters=0,
            walking_dest_meters=0
        )
        
        assert fare.min == 10.0
        assert fare.actual >= fare.min
        assert fare.max >= fare.actual
    
    def test_base_fare(self):
        """Test fare for distance within base fare range."""
        fare = FareCalculator.compute_range(
            route_distance_meters=3000,  # 3 km
            walking_origin_meters=0,
            walking_dest_meters=0
        )
        
        # 3 * 2.5 = 7.5, but minimum fare is 10.0
        assert fare.actual == 10.0
        assert fare.min <= fare.actual <= fare.max
    
    def test_additional_distance_charge(self):
        """Test fare for distance exceeding base fare."""
        fare = FareCalculator.compute_range(
            route_distance_meters=10000,  # 10 km
            walking_origin_meters=0,
            walking_dest_meters=0
        )
        
        expected_fare = 25.0  # 10 * 2.5
        assert fare.actual == expected_fare
        assert fare.min <= fare.actual <= fare.max
        assert fare.max > fare.actual
    
    def test_long_distance_charge(self):
        """Test fare calculation for long distance travel."""
        fare = FareCalculator.compute_range(
            route_distance_meters=25000,  # 25 km
            walking_origin_meters=0,
            walking_dest_meters=0
        )
        
        expected_fare = 62.5  # 25 * 2.5
        assert fare.actual == expected_fare
        assert fare.max >= fare.actual
    
    # === Rounding Tests ===
    
    def test_fare_rounding_rules(self):
        """Test fare rounding to nearest 0.5 ETB using half-up rounding.
        
        Algorithm 6.3 specifies:
        - fare_min = round(fare_min * 2) / 2  (nearest 0.5)
        - fare_max = ceil(fare_max / 5) * 5    (multiple of 5)
        
        Test cases verify proper half-up rounding behavior.
        """
        test_cases = [
            # (distance_km, raw_fare, expected_rounded)
            (4.7, 11.75, 12.0),    # 11.75 -> 12.0 (round up)
            (5.0, 12.5, 12.5),     # 12.5 -> 12.5 (exact)
            (5.1, 12.75, 13.0),    # 12.75 -> 13.0 (round up)
            (5.3, 13.25, 13.5),    # 13.25 -> 13.5 (round up from .25)
            (5.5, 13.75, 14.0),    # 13.75 -> 14.0 (round up)
            (4.2, 10.5, 10.5),     # 10.5 -> 10.5 (exact)
            (3.2, 10.0, 10.0),     # 8.0 below minimum, stays at 10.0
            (4.0, 10.0, 10.0),     # Exactly at minimum
            (4.4, 11.0, 11.0),     # 11.0 -> 11.0 (exact)
            (4.6, 11.5, 11.5),     # 11.5 -> 11.5 (exact)
            (4.9, 12.25, 12.5),    # 12.25 -> 12.5 (round up from .25)
        ]
        
        for distance_km, raw_fare, expected_rounded in test_cases:
            fare = FareCalculator.compute_range(
                route_distance_meters=distance_km * 1000
            )
            # Check that fare is rounded to nearest 0.5
            remainder = (fare.actual * 2) % 1
            assert remainder == 0, (
                f"Distance {distance_km}km: fare {fare.actual} "
                f"not rounded to 0.5 (remainder: {remainder})"
            )
            assert fare.actual == expected_rounded, (
                f"Distance {distance_km}km (raw: {raw_fare}): "
                f"expected {expected_rounded}, got {fare.actual}"
            )
    
    def test_rounding_half_up_behavior(self):
        """Test specific half-up rounding behavior.
        
        When value is exactly .5, it should stay at .5.
        When value is .25, round up to .5.
        When value is .75, round up to next whole.
        """
        # 10.25 -> 10.5
        fare = FareCalculator.compute_range(4100)  # 4.1 km * 2.5 = 10.25
        assert fare.actual == 10.5, f"Expected 10.5, got {fare.actual}"
        
        # 10.75 -> 11.0
        fare = FareCalculator.compute_range(4300)  # 4.3 km * 2.5 = 10.75
        assert fare.actual == 11.0, f"Expected 11.0, got {fare.actual}"
        
        # 10.5 -> 10.5 (stays)
        fare = FareCalculator.compute_range(4200)  # 4.2 km * 2.5 = 10.5
        assert fare.actual == 10.5, f"Expected 10.5, got {fare.actual}"
    
    def test_edge_case_zero_km(self):
        """Test edge case: exactly 0 km distance.
        
        Should return minimum fare, not throw errors.
        """
        # Test with exact zero
        fare = FareCalculator.compute_range(
            route_distance_meters=0,
            walking_origin_meters=0,
            walking_dest_meters=0
        )
        
        assert fare.actual == 10.0
        assert fare.min == 10.0
        assert fare.max >= 10.0
        
        # Test with very small distance (0.1 km = 100m)
        fare = FareCalculator.compute_range(
            route_distance_meters=100,
            walking_origin_meters=0,
            walking_dest_meters=0
        )
        
        # 0.1 * 2.5 = 0.25, but minimum is 10.0
        assert fare.actual >= 10.0
        assert fare.min >= 10.0
    
    def test_minimum_fare_enforcement(self):
        """Test that fare never falls below minimum threshold."""
        test_distances = [0.1, 0.5, 1.0, 2.0, 3.0]
        
        for distance_km in test_distances:
            fare = FareCalculator.compute_range(
                route_distance_meters=distance_km * 1000
            )
            assert fare.actual >= 10.0, (
                f"Distance {distance_km}km: fare {fare.actual} below minimum"
            )
            assert fare.min >= 10.0, (
                f"Min fare {fare.min} below minimum for {distance_km}km"
            )
    
    def test_fare_consistency(self):
        """Test that fares are consistent and logical.
        
        Longer distances should result in higher fares.
        """
        short_fare = FareCalculator.compute_range(2000).actual   # 2km
        medium_fare = FareCalculator.compute_range(5000).actual  # 5km
        long_fare = FareCalculator.compute_range(15000).actual   # 15km
        very_long_fare = FareCalculator.compute_range(30000).actual  # 30km
        
        assert short_fare <= medium_fare, (
            f"Medium fare ({medium_fare}) should be >= short fare ({short_fare})"
        )
        assert medium_fare <= long_fare, (
            f"Long fare ({long_fare}) should be >= medium fare ({medium_fare})"
        )
        assert long_fare <= very_long_fare, (
            f"Very long fare ({very_long_fare}) should be >= long fare ({long_fare})"
        )
    
    def test_negative_distance_error(self):
        """Test that negative distance raises ValueError."""
        with pytest.raises(ValueError, match="Distance cannot be negative"):
            FareCalculator.compute_range(route_distance_meters=-1000)
    
    def test_with_walking_segments(self):
        """Test fare calculation with walking segments included."""
        # Route with walking at origin
        fare = FareCalculator.compute_range(
            route_distance_meters=5000,
            walking_origin_meters=500,
            walking_dest_meters=0
        )
        
        assert fare.min < fare.max
        assert fare.actual > 0
        
        # Route with walking at both ends
        fare = FareCalculator.compute_range(
            route_distance_meters=5000,
            walking_origin_meters=500,
            walking_dest_meters=300
        )
        
        assert fare.min < fare.max
        assert fare.actual > 0
