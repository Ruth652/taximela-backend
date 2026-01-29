# In-memory POI data (no database needed)
PLACES = [
    {"name_en": "Piassa", "name_am": "ፒያሳ", "lat": 9.032558, "lon": 38.753162, "category": "landmark"},
    {"name_en": "Bole", "name_am": "ቦሌ", "lat": 9.005401, "lon": 38.763611, "category": "area"},
    {"name_en": "Merkato", "name_am": "መርካቶ", "lat": 9.030000, "lon": 38.740000, "category": "market"},
    {"name_en": "Meskel Square", "name_am": "መስቀል አደባባይ", "lat": 9.012000, "lon": 38.763000, "category": "landmark"},
    {"name_en": "4 Kilo", "name_am": "4 ኪሎ", "lat": 9.034263, "lon": 38.760698, "category": "area"},
    {"name_en": "Shola", "name_am": "ሾላ", "lat": 9.025192, "lon": 38.796031, "category": "area"},
    {"name_en": "Megenagna", "name_am": "መገናኛ", "lat": 9.020169, "lon": 38.804169, "category": "area"},
    {"name_en": "Tafo", "name_am": "ታፎ", "lat": 9.057188, "lon": 38.878122, "category": "area"},
    {"name_en": "CMC", "name_am": "ሲ.ኤም.ሲ", "lat": 9.020739, "lon": 38.850467, "category": "area"},
    {"name_en": "UK Embassy", "name_am": "የእንግሊዝ ኤምባሲ", "lat": 9.029995, "lon": 38.787304, "category": "landmark"},
    {"name_en": "Kebena", "name_am": "ከበና", "lat": 9.033981, "lon": 38.776317, "category": "area"},
    {"name_en": "Ethiopia Cinema", "name_am": "ኢትዮጵያ ሲኒማ", "lat": 9.031064, "lon": 38.754967, "category": "landmark"},
    {"name_en": "Bole Airport", "name_am": "ቦሌ አየር ማረፊያ", "lat": 8.977889, "lon": 38.799319, "category": "airport"},
    {"name_en": "Addis Ababa Stadium", "name_am": "አዲስ አበባ ስታዲየም", "lat": 9.005000, "lon": 38.763000, "category": "stadium"},
    {"name_en": "Arat Kilo", "name_am": "አራት ኪሎ", "lat": 9.034263, "lon": 38.760698, "category": "area"},
]

class PoiRepository:

    @staticmethod
    def search_places(query: str, lang: str, limit: int = 50):
        """
        Search places in memory (no database needed)
        """
        query_lower = query.lower()
        
        # Choose which name field to search
        name_field = "name_am" if lang == "am" else "name_en"
        
        # Filter places that match the query
        results = []
        for place in PLACES:
            name = place.get(name_field, "")
            if name and query_lower in name.lower():
                results.append({
                    "name": name,
                    "lat": place["lat"],
                    "lon": place["lon"],
                    "category": place["category"]
                })
                
                if len(results) >= limit:
                    break
        
        return results
