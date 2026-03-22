from infrastructure.utils.polyline_decoder import decode_polyline

# def itinerary_to_linestring_wkt(itinerary: dict):
#     """
#     Converts one itinerary's tripDetail geometries into a LINESTRING WKT.
#     Returns None if there are not enough points.
#     """
#     coords = []

#     for leg in itinerary.get("tripDetail", []):
#         encoded = leg.get("encryptedGeolocation")
#         if encoded:
#             coords.extend(decode_polyline(encoded))

#     if len(coords) < 2:
#         return None

#     points = [f"{lon} {lat}" for lat, lon in coords]
#     return f"LINESTRING({', '.join(points)})"


# def itineraries_to_multilinestring_wkt(itineraries: list[dict]):
#     """
#     Converts many itineraries into one MULTILINESTRING WKT.
#     """
#     lines = []

#     for itinerary in itineraries:
#         coords = []

#         for leg in itinerary.get("tripDetail", []):
#             encoded = leg.get("encryptedGeolocation")
#             if encoded:
#                 coords.extend(decode_polyline(encoded))

#         if len(coords) >= 2:
#             points = [f"{lon} {lat}" for lat, lon in coords]
#             lines.append(f"({', '.join(points)})")

#     if not lines:
#         return None

#     return f"MULTILINESTRING({', '.join(lines)})"


from infrastructure.utils.polyline_decoder import decode_polyline

def build_routes_wkt(itineraries):
    all_lines = []

    for itinerary in itineraries:
        for leg in itinerary["tripDetail"]:
            polyline = leg["encryptedGeolocation"]
            coords = decode_polyline(polyline)

            if len(coords) < 2:
                continue

            line = ", ".join(f"{lon} {lat}" for lat, lon in coords)
            all_lines.append(f"({line})")

    return f"MULTILINESTRING({', '.join(all_lines)})"