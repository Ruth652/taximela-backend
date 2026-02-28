
import httpx
import os

#OTP_URL = "http://localhost:8080/otp/gtfs/v1"
OTP_URL = "https://taximela-backend-1.onrender.com/otp/gtfs/v1"


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
            numItineraries: 5,
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


