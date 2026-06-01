# from sqlalchemy import text

# def get_all_routes_service_places(
#     db,  
#     routes_wkt: str,
#     radius_m: int = 300,
#     limit: int = 10,
#     cursor_distance: float | None = None,
#     cursor_id: str | None = None,
#     category_id: str | None = None
# ):
#     """
#     For ALL returned itineraries together.
#     Uses one MULTILINESTRING and paginates by distance.
#     """

#     sql = text("""
#         WITH route AS (
#             SELECT ST_SetSRID(ST_GeomFromText(:routes_wkt), 4326)::geography AS geog
#         ),
#         ranked AS (
#             SELECT
#                 b.id,
#                 b.name,
#                 b.latitude,
#                 b.longitude,
#                 b.category_id,
#                 ST_Distance(b.geom, route.geog) AS distance_m
#             FROM businesses b
#             CROSS JOIN route
#             WHERE ST_DWithin(b.geom, route.geog, :radius_m)
#         )
#         SELECT *
#         FROM ranked
#         WHERE
#             (
#                 :cursor_distance IS NULL
#                 OR distance_m > :cursor_distance
#                 OR (distance_m = :cursor_distance AND id > CAST(:cursor_id AS uuid))
#             )
#         ORDER BY distance_m ASC, id ASC
#         LIMIT :limit
#     """)

#     rows = db.execute(
#         sql,
#         {
#             "routes_wkt": routes_wkt,
#             "radius_m": radius_m,
#             "limit": limit,
#             "cursor_distance": cursor_distance,
#             "cursor_id": cursor_id,
#         }
#     ).mappings().all()

#     items = [
#         {
#             "id": str(row["id"]),
#             "name": row["name"],
#             "latitude": float(row["latitude"]),
#             "longitude": float(row["longitude"]),
#             "category_id": str(row["category_id"]) if row["category_id"] else None,
#             "distance_m": float(row["distance_m"]),
#         }
#         for row in rows
#     ]

#     next_cursor = None
#     if items:
#         last = items[-1]
#         next_cursor = {
#             "distance": last["distance_m"],
#             "id": last["id"]
#         }

#     return {
#         "items": items,
#         "next_cursor": next_cursor
#     }




from sqlalchemy import text

def get_all_routes_service_places(
    db,
    routes_wkt: str,
    radius_m: int = 300,
    limit: int = 10,
    cursor_distance: float | None = None,
    cursor_id: str | None = None,
    category_id: str | None = None
):
    """
    For ALL returned itineraries together.
    Uses one MULTILINESTRING and paginates by distance.
    """

    sql = text("""
        WITH route AS (
            SELECT ST_SetSRID(ST_GeomFromText(:routes_wkt), 4326)::geography AS geog
        ),
        ranked AS (
            SELECT
                b.id,
                b.name,
                b.latitude,
                b.longitude,
                b.category_id,
                b.is_featured,
                b.featured_until,
                b.business_logo,
                ST_Distance(b.geom, route.geog) AS distance_m
            FROM businesses b
            CROSS JOIN route
            WHERE 
                ST_DWithin(b.geom, route.geog, :radius_m)
                AND (
                    :category_id IS NULL
                    OR b.category_id = CAST(:category_id AS uuid)
                )
        )
        SELECT *
        FROM ranked
        WHERE
            (
                :cursor_distance IS NULL
                OR distance_m > :cursor_distance
                OR (distance_m = :cursor_distance AND id > CAST(:cursor_id AS uuid))
            )
        ORDER BY
            CASE WHEN is_featured = true AND (featured_until IS NULL OR featured_until > NOW()) THEN 0 ELSE 1 END ASC,
            distance_m ASC,
            id ASC
        LIMIT :limit
    """)

    rows = db.execute(
        sql,
        {
            "routes_wkt": routes_wkt,
            "radius_m": radius_m,
            "limit": limit,
            "cursor_distance": cursor_distance,
            "cursor_id": cursor_id,
            "category_id": category_id,
        }
    ).mappings().all()

    items = [
        {
            "id": str(row["id"]),
            "name": row["name"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "category_id": str(row["category_id"]) if row["category_id"] else None,
            "distance_m": float(row["distance_m"]),
            "is_featured": bool(row["is_featured"]),
            "business_logo": row["business_logo"],
        }
        for row in rows
    ]

    next_cursor = None
    if items:
        last = items[-1]
        next_cursor = {
            "distance": last["distance_m"],
            "id": last["id"]
        }

    return {
        "items": items,
        "next_cursor": next_cursor
    }