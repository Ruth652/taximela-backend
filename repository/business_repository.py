from domain.business_model import Business
from domain.business_category_model import BusinessCategory
from domain.user_model import User
#from datetime import datetime


class BusinessRepository:

    def __init__(self, db):
        self.db = db

    def create_business_from_registration(self, registration, admin_id):

        business = Business(
            owner_id=registration.user_id,
            name=registration.business_name,
            latitude=registration.latitude,
            longitude=registration.longitude,
            government_id_fan=registration.government_id_fan,
            government_id_photo_url=registration.government_id_photo_url,
            license_photo_url=registration.business_license_photo_url,
            category_id=registration.category_id,
            #approved_at= datetime.utcnow(),
            approved_by=admin_id
        )

        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)

        return business
    def get_filtered_registrations(
        self,
        status,
        user_id,
        from_date,
        to_date,
        search,
        page,
        limit
    ):

        query = (
            self.db.query(Business)
            .join(Business.owner)
            .join(Business.category)
        )
        # use outer join if you want to include businesses without a category(but if i do that i need to handle the case where category is None in the search filter)

        if user_id:
            query = query.filter(Business.owner_id == user_id)

        if status:
            query = query.filter(Business.status == status)

        if from_date:
            query = query.filter(Business.created_at >= from_date)

        if to_date:
            query = query.filter(Business.created_at <= to_date)

        if search:
            query = query.filter(BusinessCategory.name.ilike(f"%{search}%"))

        total = query.count()

        records = (
            query.order_by(Business.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "data": [
                {
                    "id": r.id,
                    "business_name": r.name,
                    "owner_name": r.owner.full_name,
                    "owner_profile_picture_url": r.owner.profile_picture_url,
                    "status": r.status,
                    "category": r.category.name if r.category else None,
                    "category_id": r.category_id,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                }
                for r in records
            ],
            "total": total,
            "page": page,
            "limit": limit,
        }
    
    def get_business_by_id(self, business_id):
        print(f"Fetching business with ID: {business_id}")
        return self.db.query(Business).filter(Business.id == business_id).first()
    def get_nearby_businesses_for_routes(
            self,
            routes_wkt: str,
            radius_m: int = 300,
            limit: int = 10,
            cursor_distance: float | None = None,
            cursor_id: str | None = None
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
                        ST_Distance(b.geom, route.geog) AS distance_m
                    FROM businesses b
                    CROSS JOIN route
                    WHERE ST_DWithin(b.geom, route.geog, :radius_m)
                )
                SELECT *
                FROM ranked
                WHERE
                    (
                        :cursor_distance IS NULL
                        OR distance_m > :cursor_distance
                        OR (distance_m = :cursor_distance AND id > CAST(:cursor_id AS uuid))
                    )
                ORDER BY distance_m ASC, id ASC
                LIMIT :limit
            """)

            rows = self.db.execute(
                sql,
                {
                    "routes_wkt": routes_wkt,
                    "radius_m": radius_m,
                    "limit": limit,
                    "cursor_distance": cursor_distance,
                    "cursor_id": cursor_id,
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