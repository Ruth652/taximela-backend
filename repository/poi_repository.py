from sqlalchemy import text
from infrastructure.database import SessionLocal

class PoiRepository:

    @staticmethod
    def search_places(query: str, lang: str, limit: int = 50):
        session = SessionLocal()
        try:
            q = f"%{query}%"

            if lang == "am":
                name_column = "name_am"
            else:
                name_column = "name_en"

            sql = text(f"""
                SELECT {name_column} AS name, lat, lon, category
                FROM poi
                WHERE {name_column} IS NOT NULL
                AND {name_column} ILIKE :q
                LIMIT :limit
            """)

            rows = session.execute(sql, {"q": q, "limit": limit})

            return [
                {
                    "name": r.name,
                    "lat": float(r.lat),
                    "lon": float(r.lon),
                    "category": r.category
                }
                for r in rows
            ]
        finally:
            session.close()
