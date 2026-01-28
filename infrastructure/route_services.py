# # infrastructure/example_services.py

# import httpx

# OTP_URL = "http://localhost:8080/otp/gtfs/v1"

# async def fetch_route_from_otp(from_lat, from_lon, to_lat, to_lon, date, time):
#     query = {
#         "query": """
#         {
#           plan(
#             from: {lat: %f, lon: %f},
#             to: {lat: %f, lon: %f},
#             date: "%s",
#             time: "%s",
            
#           ) {
#             itineraries {
#               duration
#               walkDistance
#               numberOfTransfers
#               legs {
#                 mode
#                 startTime
#                 endTime
#                 from { name lat lon }
#                 to { name lat lon }
#                 route { shortName longName }
#                 legGeometry {
#                   points
#                   length
#                 }
#               }
#             }
#           }
#         }
#         """ % (from_lat, from_lon, to_lat, to_lon, date, time)
#     }

#     timeout = httpx.Timeout(60.0, connect=10.0)  
#     async with httpx.AsyncClient() as client:
#         response = await client.post(OTP_URL, json=query)
#         response.raise_for_status()
#         return response.json()



# infrastructure/example_services.py

import httpx

OTP_URL = "http://localhost:8080/otp/gtfs/v1"

async def fetch_route_from_otp(from_lat, from_lon, to_lat, to_lon, date, time):
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


    timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(OTP_URL, json=query)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Catch network errors, timeouts, and HTTP status errors
            return {"error": str(e)}
