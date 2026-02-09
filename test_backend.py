import requests
import json
from datetime import datetime

print("=" * 70)
print("TAXIMELA BACKEND - COMPREHENSIVE TEST SUITE")
print("=" * 70)

BASE_URL = "http://localhost:8000"

# Test 1: Health Check
print("\n" + "=" * 70)
print("TEST 1: Health Check")
print("=" * 70)

try:
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        print("✅ PASSED - Backend is running")
    else:
        print("❌ FAILED")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Route Planning - Walking
print("\n" + "=" * 70)
print("TEST 2: Route Planning - Walking (Megenagna to Piassa)")
print("=" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/api/plan",
        json={
            "from_lat": 9.020169,
            "from_lon": 38.804169,
            "to_lat": 9.032558,
            "to_lon": 38.753162,
            "date": "2026-01-29",
            "time": "10:30:00"
        }
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Found {len(data)} route option(s)")
            
            for i, route in enumerate(data[:2], 1):
                print(f"\n--- Route Option {i} ---")
                print(f"Duration: {route.get('duration', 0) // 60} minutes")
                print(f"Walk Distance: {route.get('walkDistance', 0):.2f} meters")
                print(f"Number of Transfers: {route.get('numberOfTransfers', 'N/A')}")
                
                legs = route.get('legs', [])
                print(f"Legs: {len(legs)}")
                
                for j, leg in enumerate(legs, 1):
                    mode = leg.get('mode', 'UNKNOWN')
                    distance = leg.get('distance', 0)
                    print(f"  Leg {j}: {mode} - {distance:.0f}m")
                    
                    if mode == 'BUS':
                        route_info = leg.get('route', {})
                        print(f"    Bus: {route_info.get('shortName', 'N/A')} - {route_info.get('longName', 'N/A')}")
            
            print("\n✅ PASSED - Route planning works")
        else:
            print("⚠️ WARNING - No routes found")
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"❌ FAILED - Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Route Planning - Transit (Shola to Piassa)
print("\n" + "=" * 70)
print("TEST 3: Route Planning - Transit (Shola to Piassa - Bus 101)")
print("=" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/api/plan",
        json={
            "from_lat": 9.025192,
            "from_lon": 38.796031,
            "to_lat": 9.032558,
            "to_lon": 38.753162,
            "date": "2026-01-29",
            "time": "08:00:00"
        }
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Found {len(data)} route option(s)")
            
            has_bus = False
            for route in data:
                for leg in route.get('legs', []):
                    if leg.get('mode') in ['BUS', 'TRANSIT']:
                        has_bus = True
                        break
            
            if has_bus:
                print("✅ PASSED - Transit routing works")
            else:
                print("⚠️ WARNING - Only walking routes found (no bus schedules)")
        else:
            print("⚠️ WARNING - No routes found")
    else:
        print(f"❌ FAILED - Status {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: POI Search
print("\n" + "=" * 70)
print("TEST 4: POI Search")
print("=" * 70)

try:
    response = requests.get(f"{BASE_URL}/api/poi/search?query=piassa&lang=en")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} POI(s)")
        
        for poi in data[:3]:
            print(f"  - {poi.get('name', 'N/A')} ({poi.get('lat', 0)}, {poi.get('lon', 0)})")
        
        print("✅ PASSED - POI search works")
    else:
        print(f"⚠️ Status {response.status_code} - POI search may need database")
        
except Exception as e:
    print(f"⚠️ POI search not available: {e}")

# Test 5: Reverse Geocoding
print("\n" + "=" * 70)
print("TEST 5: Reverse Geocoding")
print("=" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/reverse-geocode",
        json={
            "lat": 9.020293,
            "lng": 38.80172
        }
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Place Name: {data.get('name', 'N/A')}")
        print("✅ PASSED - Reverse geocoding works")
    else:
        print(f"❌ FAILED - Status {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 6: Response Format Validation
print("\n" + "=" * 70)
print("TEST 6: Response Format Validation")
print("=" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/api/plan",
        json={
            "from_lat": 9.020169,
            "from_lon": 38.804169,
            "to_lat": 9.026519,
            "to_lon": 38.75287,
            "date": "2026-01-29",
            "time": "10:30:00"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            route = data[0]
            
            # Check required fields
            required_fields = ['duration', 'walkDistance', 'numberOfTransfers', 'legs']
            missing_fields = [f for f in required_fields if f not in route]
            
            if not missing_fields:
                print("✅ All required fields present:")
                print(f"  - duration: {route['duration']}")
                print(f"  - walkDistance: {route['walkDistance']}")
                print(f"  - numberOfTransfers: {route['numberOfTransfers']}")
                print(f"  - legs: {len(route['legs'])} leg(s)")
                
                # Check leg structure
                if route['legs']:
                    leg = route['legs'][0]
                    leg_fields = ['mode', 'startTime', 'endTime', 'from', 'to', 'legGeometry']
                    missing_leg_fields = [f for f in leg_fields if f not in leg]
                    
                    if not missing_leg_fields:
                        print("✅ Leg structure correct")
                        print("✅ PASSED - Response format matches target")
                    else:
                        print(f"⚠️ Missing leg fields: {missing_leg_fields}")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        else:
            print("⚠️ No routes to validate")
    else:
        print(f"❌ FAILED - Status {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ = Passed")
print("⚠️ = Warning/Partial")
print("❌ = Failed")
print("\nAll critical tests should show ✅")
print("=" * 70)
