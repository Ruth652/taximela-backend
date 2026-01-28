import requests

def reverse_geocode(lat: float, lng: float):
    url = (
        "https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lng}&format=json&addressdetails=1"
    )

    headers = {
        "User-Agent": "TaxiMela-App"  
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        address = data.get("address", {})

        road = address.get("road")
        neighbourhood = address.get("neighbourhood") or address.get("suburb")
        city = address.get("city") or address.get("town") or address.get("village")
        country = address.get("country")

        parts = [p for p in [road, neighbourhood, city, country] if p]
        return ", ".join(parts) if parts else data.get("display_name")

    except Exception as e:
        print("Geocoding error:", e)
        return None
