from requests import Session

from domain.admin_model import Admin
from domain.route_otp_model import Routes
from domain.stops_model import Stops


class OTPRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_stops(self):
         return self.db.query(Stops).all()

    def get_stops_by_id(self, stops_id: int):
        return self.db.query(Stops).filter(Stops.stop_id == stops_id).first()
    
    def get_routes(self):
        return self.db.query(Routes).all()  
    
    def get_routes_by_id(self, route_id: int):
        return self.db.query(Routes).filter(Routes.route_id == route_id).first()