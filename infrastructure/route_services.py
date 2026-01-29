import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OTP_BASE_URL = os.getenv("OTP_URL", "http://localhost:8080")

async def fetch_route_from_otp(from_lat, from_lon, to_lat, to_lon, date, time):
    """
    Fetch route from OTP using REST API
    """
    try:
        url = f"{OTP_BASE_URL}/otp/routers/default/plan"
        
        # Convert time format from HH:MM:SS to HH:MMam/pm
        # e.g., "10:30:00" -> "10:30am"
        if ":" in time:
            parts = time.split(":")
            hour = int(parts[0])
            minute = parts[1]
            period = "am" if hour < 12 else "pm"
            if hour > 12:
                hour -= 12
            elif hour == 0:
                hour = 12
            time = f"{hour}:{minute}{period}"
        
        params = {
            "fromPlace": f"{from_lat},{from_lon}",
            "toPlace": f"{to_lat},{to_lon}",
            "time": time,
            "date": date,
            "mode": "TRANSIT,WALK",
            "maxWalkDistance": 5000,
            "numItineraries": 3
        }
        
        print(f"Calling OTP: {url}")
        print(f"Params: {params}")
        
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e), "plan": {"itineraries": []}}
