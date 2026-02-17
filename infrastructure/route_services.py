
import httpx
import os

OTP_URL = "http://localhost:8080/otp/gtfs/v1"
# OTP_URL = os.getenv("OTP_BASE_URL")

# async def fetch_route_from_otp(from_lat, from_lon, to_lat, to_lon, time = "06:00:00"):
#     query = {
#         "query": f"""
#         {{
#         plan(
#             from: {{lat: {from_lat}, lon: {from_lon}}},
#             to: {{lat: {to_lat}, lon: {to_lon}}},
#             date: "2026-01-15",
#             time: "{time}",
#             numItineraries: 999,
#             searchWindow: 86400,
#             maxTransfers: 5,
#             maxWalkDistance: 5000,
#             transportModes: [
#             {{mode: WALK}},
#             {{mode: TRANSIT}}
#             ]
#         ) {{
#             itineraries {{
#             duration
#             walkDistance
#             numberOfTransfers
#             legs {{
#                 mode
#                 startTime
#                 endTime
#                 from {{ name lat lon }}
#                 to {{ name lat lon }}
#                 route {{ shortName longName }}
#                 distance
#                 legGeometry {{
#                 points
#                 length
#                 }}
#             }}
#             }}
#         }}
#         }}
#         """
#     }



async def fetch_route_from_otp(from_lat, from_lon, to_lat, to_lon, time="06:00:00"):
    """
    Fetch route from OTP using GraphQL API
    Date is hardcoded.
    """

    query = {
        "query": f"""
        {{
          plan(
            from: {{lat: {from_lat}, lon: {from_lon}}},
            to: {{lat: {to_lat}, lon: {to_lon}}},
            date: "2026-01-15",
            time: "{time}",
            numItineraries: 999,
            searchWindow: 86400,
            maxTransfers: 5,
            maxWalkDistance: 5000,
            transportModes: [
              {{mode: WALK}},
              {{mode: TRANSIT}}
            ]
          ) {{
            itineraries {{
              duration
              walkDistance
              numberOfTransfers
              legs {{
                mode
                startTime
                endTime
                from {{ name lat lon }}
                to {{ name lat lon }}
                route {{ shortName longName }}
                distance
                legGeometry {{
                  points
                  length
                }}
              }}
            }}
          }}
        }}
        """
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OTP_URL, json=query)

            response.raise_for_status()

            return response.json()

    except httpx.HTTPError as e:
        return {"error": str(e)}



# async def fetch_route_from_otp(from_lat, from_lon, to_lat, to_lon, date, time):
#     """
#     Fetch route from OTP using REST API
#     """
#     try:
#         url = f"{OTP_BASE_URL}/otp/routers/default/plan"
        
#         # Convert time format from HH:MM:SS to HH:MMam/pm
#         # e.g., "10:30:00" -> "10:30am"
#         if ":" in time:
#             parts = time.split(":")
#             hour = int(parts[0])
#             minute = parts[1]
#             period = "am" if hour < 12 else "pm"
#             if hour > 12:
#                 hour -= 12
#             elif hour == 0:
#                 hour = 12
#             time = f"{hour}:{minute}{period}"
        
#         params = {
#             "fromPlace": f"{from_lat},{from_lon}",
#             "toPlace": f"{to_lat},{to_lon}",
#             "time": time,
#             "date": date,
#             "mode": "TRANSIT,WALK",
#             "maxWalkDistance": 5000,
#             "numItineraries": 3
#         }
        
#         print(f"Calling OTP: {url}")
#         print(f"Params: {params}")
        
#         timeout = httpx.Timeout(60.0, connect=10.0)
#         async with httpx.AsyncClient(timeout=timeout) as client:
#             response = await client.get(url, params=params)
#             print(f"Response status: {response.status_code}")
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPError as e:
#             # Catch network errors, timeouts, and HTTP status errors
#             return {"error": str(e)}


