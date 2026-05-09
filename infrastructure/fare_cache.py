import time
from sqlalchemy.orm import Session
from domain.fare_configurations_model import FareConfiguration
from datetime import datetime

class FareCache:
    _instance = None
    _fare_data = None
    _last_updated = 0
    _ttl = 3600  # Automatically refresh every 1 hour as a safety measure

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FareCache, cls).__new__(cls)
        return cls._instance

    def get_fare(self, db: Session) -> FareConfiguration:
        """
        Retrieves the currently active fare configuration.
        Uses memory cache if available and not expired.
        """
        now = time.time()
        
        # Refresh if cache is empty or TTL has expired
        if self._fare_data is None or (now - self._last_updated > self._ttl):
            # Query the DB for the single row marked as active
            active_fare = db.query(FareConfiguration).filter(
                FareConfiguration.is_active == True
            ).first()
            
            if active_fare:
                self._fare_data = active_fare
                self._last_updated = now
                print(f"--- [FareCache] Refreshed: {active_fare.base_fare_etb} ETB Base ---")
            else:
                # Fallback or warning if no active fare is found in DB
                print("--- [FareCache] WARNING: No active fare configuration found! ---")
        
        return self._fare_data

    def invalidate(self):
        """
        Force the cache to clear. 
        Call this in the Admin Router after updating a fare.
        """
        self._fare_data = None
        self._last_updated = 0
        print("--- [FareCache] Cache Invalidated ---")

# Global singleton instance to be imported by usecases
fare_cache = FareCache()