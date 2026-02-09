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
       

        return Contribution(
            user_id=data.user_id,
            target_type=data.target_type,
            target_id=data.target_id,
            description=data.description
        )
