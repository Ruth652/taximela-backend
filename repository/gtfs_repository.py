


from requests import Session

from domain.gtfs_model import GTFS


class GTFSRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add_to_gtfs_queue(self, db, contribution_id: int, queued_by: str):
        gtfs_entry = GTFS(
            contribution_id=contribution_id,
            queued_by=queued_by
        )
        db.add(gtfs_entry)
        db.commit()
        db.refresh(gtfs_entry)
        return gtfs_entry

    
    
    