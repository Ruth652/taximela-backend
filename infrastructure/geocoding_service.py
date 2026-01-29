import requests
import time

def reverse_geocode(lat: float, lng: float, lang: str = "en"):
    """
    Reverse geocode coordinates to place name
    
    Args:
        lat: Latitude
        lng: Longitude
        lang: Language code ("en" for English, "am" for Amharic)
    """
    url = (
        "https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lng}&format=json&addressdetails=1"
    )

    headers = {
        "User-Agent": "TaxiMela-App/1.0",
        "Accept-Language": lang  # Force language
    }

    try:
        # Add small delay to respect rate limits
        time.sleep(1)
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if request was successful
        if response.status_code != 200:
            print(f"Geocoding API error: {response.status_code}")
            return f"Location ({lat}, {lng})"
        
        data = response.json()
        
        # Check if we got an error from API
        if "error" in data:
            print(f"Geocoding error: {data.get('error')}")
            return f"Location ({lat}, {lng})"
        
        address = data.get("address", {})

        road = address.get("road")
        neighbourhood = address.get("neighbourhood") or address.get("suburb")
        city = address.get("city") or address.get("town") or address.get("village")
        country = address.get("country")

        parts = [p for p in [road, neighbourhood, city, country] if p]
        
        if parts:
            return ", ".join(parts)
        elif data.get("display_name"):
            return data.get("display_name")
        else:
            # Fallback to coordinates
            return f"Location ({lat:.6f}, {lng:.6f})"

    except requests.Timeout:
        print("Geocoding timeout")
        return f"Location ({lat:.6f}, {lng:.6f})"
    except Exception as e:
        print(f"Geocoding error: {e}")
        return f"Location ({lat:.6f}, {lng:.6f})"
