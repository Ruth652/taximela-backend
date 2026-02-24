class Contribution:
    @staticmethod
    def create(data):
        action = data.description.get("action")

        if data.target_type == "station":
            if action == "CREATE":
                if "lat" not in data.description or "lon" not in data.description:
                    raise ValueError("Station creation requires lat and lon")

            if action == "MOVE":
                if "lat" not in data.description or "lon" not in data.description:
                    raise ValueError("Station move requires lat and lon")

            if action == "RENAME":
                if "new_name" not in data.description:
                    raise ValueError("Station rename requires new_name")
                
            if action == "DELETE":
                if not data.target_id:
                    raise ValueError("Station deletion requires target_id")
                else:
                    # For deletion, we might want to check if the station exists before allowing the contribution
                    # This would require access to the station repository, which is not available in this context
                    pass
            else:
                raise ValueError(f"Unsupported action for station: {action}")
            
        elif data.target_type == "route":
            if action == "CREATE":
                # I need to define what fields are required for route creation in the description, such as start and end points, or a list of waypoints
                pass
            if action == "MOVE":
                # Similar to station move, we would need new coordinates or waypoints for the route
                pass
            if action == "DELETE":
                if not data.target_id:
                    raise ValueError("Route deletion requires target_id")
                else:
                    # Similar to station deletion, we might want to check if the route exists
                    pass
       

        return Contribution(
            user_id=data.user_id,
            target_type=data.target_type,
            target_id=data.target_id,
            description=data.description,
            status=data.status,
        )
