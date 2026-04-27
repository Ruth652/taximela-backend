from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.shape_model import Shapes
from domain.stop_times_model import StopTimes
from domain.trips_model import Trips
from repository.contribution_group_repository import ContributionGroupRepository
from schemas.contribution_group import ApproveContributionGroupRequest

from domain.stops_model import Stops
from domain.route_otp_model import Routes


class ContributionGroupUseCase:

    def __init__(self, repo: ContributionGroupRepository, otp_db: Session):
        self.repo = repo
        self.otp_db = otp_db

    #GET PAGINATED GROUPS
    def get_groups(
        self,
        page: int,
        limit: int,
        target_type: str = None,
        action: str = None
    ):
        total, results = self.repo.get_paginated_groups(
            page=page,
            limit=limit,
            target_type=target_type,
            action=action
        )

        data = [
            {
                "group_id": row.group_id,
                "target_type": row.target_type,
                "action": row.action,
                "target_id": row.target_id,
                "contribution_count": row.contribution_count,
                "latest_contribution_at": row.latest_contribution_at,
                "reference_stops": row.reference_stops,
            }
            for row in results
        ]

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "data": data
        }

    # GET GROUP BY ID
    def get_group_by_id(self, group_id: int):
        group = self.repo.get_group_by_id(group_id)

        if not group:
            return None

        contributions_data = [
            {
                "id": c.id,
                "user_id": c.user_id,
                "target_type": c.target_type,
                "action": c.action,
                "target_id": c.target_id,
                "payload": c.payload,
                "status": c.status,
                "created_at": c.created_at,
            }
            for c in group.contributions
        ]

        return {
            "group_id": group.id,
            "target_type": group.target_type,
            "action": group.action,
            "target_id": group.target_id,
            "reference_stops": group.reference_stops,
            "contributions": contributions_data
        }

    def approve_group(self, request: ApproveContributionGroupRequest):
        group = self.repo.get_group_by_id(request.group_id)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        handlers = {
            "station": self._handle_station,
            "route": self._handle_route,
        }

        handler = handlers.get(group.target_type)

        if not handler:
            raise HTTPException(status_code=400, detail="Unsupported target type")

        try:
            handler(group, request.final_payload)
            self.otp_db.commit()
            
        except Exception:
            self.otp_db.rollback()
            raise

        return {"message": "Approved successfully"}

    # ======================
    # HANDLERS (LOGIC LAYER)
    # ======================

    def _handle_station(self, group, data: dict):
        db = self.otp_db

        if group.action == "new":

            lat = group.reference_lat
            lon = group.reference_lon

            if not group.contributions:
                raise HTTPException(status_code=400, detail="No contributions found")

            latest_contribution = max(group.contributions, key=lambda c: c.created_at)

            name = latest_contribution.payload.get("name")

            if not name:
                raise HTTPException(status_code=400, detail="Name not found in payload")

            station = Stops(
                stop_name=name,
                stop_lat=lat,
                stop_lon=lon
            )
            
            db.add(station)

        elif group.action == "edit":
            station = db.get(Stops, group.target_id)

            if not station:
                raise HTTPException(status_code=404, detail="Station not found")

            data = data or {}  # handle None safely

            if "stop_name" in data:
                station.stop_name = data["stop_name"]

            if "stop_lat" in data:
                station.stop_lat = data["stop_lat"]
                
            elif getattr(group, "reference_lat", None) is not None:
                station.stop_lat = group.reference_lat

            if "stop_lon" in data:
                station.stop_lon = data["stop_lon"]
                
            elif getattr(group, "reference_lon", None) is not None:
                station.stop_lon = group.reference_lon
                

        elif group.action == "delete":
            station = db.get(Stops, group.target_id)

            if not station:
                raise HTTPException(status_code=404, detail="Station not found")
            print(f"Deleting station {station.stop_id} - {station.stop_name}")
            
            stop_id = station.stop_id

            # 🔥 Get ALL stop_times for this stop
            stop_times = db.query(StopTimes).filter(
                StopTimes.stop_id == stop_id
            ).all()

            # Collect affected trips
            affected_trip_ids = {st.trip_id for st in stop_times}

            for trip_id in affected_trip_ids:

                # Get all stop_times for this trip
                trip_stop_times = db.query(StopTimes).filter(
                    StopTimes.trip_id == trip_id
                ).order_by(StopTimes.stop_sequence).all()

                total_stops = len(trip_stop_times)

                # Case 1: deleting this stop makes trip invalid
                if total_stops - 1 < 2:
                    trip = db.get(Trips, trip_id)
                    

                    if trip:
                        route_id = trip.route_id
                        print(f"Trip {trip_id} will be deleted as it has less than 2 stops after deletion")

                        # delete all stop_times of this trip
                        db.query(StopTimes).filter(
                            StopTimes.trip_id == trip_id
                        ).delete()

                        # delete trip
                        db.delete(trip)

                        # check if route still has trips
                        remaining_trips = db.query(Trips).filter(
                            Trips.route_id == route_id
                        ).count()

                        if remaining_trips == 0:
                            route = db.get(Routes, route_id)
                            
                            if route:
                                print(f"Route {route_id} will be deleted as it has no more trips")
                                db.delete(route)

                # Case 2: trip still valid → remove stop + reorder
                else:
                    # delete the specific stop_time
                    db.query(StopTimes).filter(
                        StopTimes.trip_id == trip_id,
                        StopTimes.stop_id == stop_id
                    ).delete()

                    # get updated stop_times
                    remaining = db.query(StopTimes).filter(
                        StopTimes.trip_id == trip_id
                    ).order_by(StopTimes.stop_sequence).all()

                    # 🔥 reassign stop_sequence
                    for index, st in enumerate(remaining, start=1):
                        st.stop_sequence = index
                    
                    

            # 🔥 finally delete the station itself
            db.delete(station)

    def _handle_route(self, group, data: dict):
        db = self.otp_db

        if not data:
            raise HTTPException(status_code=400, detail="No route data provided")
        
        if group.action in ["edit", "delete"] and not group.target_id:
            raise HTTPException(status_code=400, detail="Target ID required for edit/delete")
        
        if group.action != "delete":
            route_data = data.get("route")
            trips_data = data.get("trips", [])

            if not route_data:
                raise HTTPException(status_code=400, detail="Route data missing")

        # -------------------------
        # CREATE ROUTE
        # -------------------------
        if group.action == "new":
            route = Routes(
                route_short_name=route_data.get("route_short_name"),
                route_long_name=route_data.get("route_long_name"),
                route_type=3
            )
            db.add(route)
            db.flush()

            route_id = route.route_id

        # -------------------------
        # EDIT ROUTE
        # -------------------------
        elif group.action == "edit":
            route = db.get(Routes, group.target_id)

            if not route:
                raise HTTPException(status_code=404, detail="Route not found")

            route_id = route.route_id

            # update basic fields only
            if "route_short_name" in route_data:
                route.route_short_name = route_data["route_short_name"]

            if "route_long_name" in route_data:
                route.route_long_name = route_data["route_long_name"]

            # OPTIONAL: only rebuild trips if explicitly requested
            if data.get("rebuild", False):
                trips = db.query(Trips).filter(Trips.route_id == route_id).all()

                shape_ids = set()

                for trip in trips:
                    shape_ids.add(trip.shape_id)

                    db.query(StopTimes).filter(
                        StopTimes.trip_id == trip.trip_id
                    ).delete()

                db.query(Trips).filter(Trips.route_id == route_id).delete()

                db.query(Shapes).filter(
                    Shapes.shape_id.in_(shape_ids)
                ).delete(synchronize_session=False)

        # -------------------------
        # DELETE ROUTE
        # -------------------------
        elif group.action == "delete":
            route = db.get(Routes, group.target_id)

            if not route:
                raise HTTPException(status_code=404, detail="Route not found")

            route_id = route.route_id

            trips = db.query(Trips).filter(Trips.route_id == route_id).all()

            shape_ids = set()

            for trip in trips:
                shape_ids.add(trip.shape_id)

                db.query(StopTimes).filter(
                    StopTimes.trip_id == trip.trip_id
                ).delete()

            db.query(Trips).filter(Trips.route_id == route_id).delete()

            db.query(Shapes).filter(
                Shapes.shape_id.in_(shape_ids)
            ).delete(synchronize_session=False)

            db.delete(route)
            return

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        # -------------------------
        # CREATE TRIPS (core logic)
        # -------------------------
        for trip_data in trips_data:
            # ---- SHAPE (per trip or shared) ----
            shape_points = trip_data.get("shape", [])

            shape_id = None

            if shape_points:
                shape_id = str(uuid.uuid4())

                for i, pt in enumerate(shape_points):
                    db.add(Shapes(
                        shape_id=shape_id,
                        shape_pt_lat=pt["lat"],
                        shape_pt_lon=pt["lon"],
                        shape_pt_sequence=i + 1,
                        shape_dist_traveled=pt.get("dist", 0)
                    ))

            # ---- CREATE TRIP ----
            trip = Trips(
                route_id=route_id,
                service_id=trip_data.get("service_id", "everyday"),
                trip_id=str(uuid.uuid4()),
                trip_headsign=trip_data.get("headsign"),
                shape_id=shape_id,
                direction_id=trip_data.get("direction_id", 0)
            )
            db.add(trip)
            db.flush()

            trip_id = trip.trip_id

            # ---- STOP TIMES (per trip) ----
            stops = trip_data.get("stops", [])

            if not stops:
                raise HTTPException(
                    status_code=400,
                    detail=f"Trip {trip_id} has no stops"
                )
           
            interval = timedelta(minutes=10)
            
            prev_time = None

            for i, stop in enumerate(stops):
                if stop.get("arrival_time"):
                    current_time = datetime.strptime(stop["arrival_time"], "%H:%M:%S")
                else:
                    if prev_time is None:
                        current_time = datetime.strptime("06:00:00", "%H:%M:%S")
                    else:
                        current_time = prev_time + interval

                time_str = current_time.strftime("%H:%M:%S")
                prev_time = current_time

                db.add(StopTimes(
                    trip_id=trip_id,
                    stop_id=stop["stop_id"],
                    stop_sequence=i + 1,
                    arrival_time=stop.get("arrival_time") or time_str,
                    departure_time=stop.get("departure_time") or time_str
                ))