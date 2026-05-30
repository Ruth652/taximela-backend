from fastapi import HTTPException
from repository.notification_repository import NotificationRepository
from repository.auth_identity_repository import AuthIdentityRepository
from repository.admin_repository import AdminRepository
import uuid


def get_notifications_usecase(db, firebase_uid: str, page: int, limit: int):
    auth_repo = AuthIdentityRepository(db)
    admin_repo = AdminRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

    admin = admin_repo.get_admin_by_firebase_uid(firebase_uid)
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    repo = NotificationRepository(db)
    result = repo.get_notifications_for_admin(admin.id, page, limit)

    return {
        "notifications": [
            {
                "id": str(n.id),
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "timestamp": n.created_at.isoformat() + "Z",
                "read": n.read,
                "action_url": n.action_url,
                "priority": n.priority,
            }
            for n in result["notifications"]
        ],
        "total_count": result["total_count"],
        "unread_count": result["unread_count"],
    }


def mark_notifications_read_usecase(db, firebase_uid: str, notification_ids: list[str]):
    admin_repo = AdminRepository(db)

    admin = admin_repo.get_admin_by_firebase_uid(firebase_uid)
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    uuids = []
    for nid in notification_ids:
        try:
            uuids.append(uuid.UUID(nid))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid UUID: {nid}")

    repo = NotificationRepository(db)
    repo.mark_as_read(admin.id, uuids)
    return {"message": "Notifications marked as read"}


def mark_all_notifications_read_usecase(db, firebase_uid: str):
    admin_repo = AdminRepository(db)

    admin = admin_repo.get_admin_by_firebase_uid(firebase_uid)
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    repo = NotificationRepository(db)
    repo.mark_all_as_read(admin.id)
    return {"message": "All notifications marked as read"}
