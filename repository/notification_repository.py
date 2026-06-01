from sqlalchemy.orm import Session
from domain.notification_model import Notification
from domain.admin_model import Admin
import uuid


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        admin_id: uuid.UUID,
        type: str,
        title: str,
        message: str,
        priority: str = "medium",
        action_url: str = None,
    ) -> Notification:
        notification = Notification(
            admin_id=admin_id,
            type=type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
        )
        self.db.add(notification)
        self.db.flush()
        return notification

    def get_notifications_for_admin(self, admin_id: uuid.UUID, page: int = 1, limit: int = 20):
        offset = (page - 1) * limit
        query = self.db.query(Notification).filter(
            Notification.admin_id == admin_id
        ).order_by(Notification.created_at.desc())

        total_count = query.count()
        unread_count = query.filter(Notification.read == False).count()
        notifications = query.offset(offset).limit(limit).all()

        return {
            "notifications": notifications,
            "total_count": total_count,
            "unread_count": unread_count,
        }

    def mark_as_read(self, admin_id: uuid.UUID, notification_ids: list[uuid.UUID]):
        self.db.query(Notification).filter(
            Notification.admin_id == admin_id,
            Notification.id.in_(notification_ids),
        ).update({"read": True}, synchronize_session=False)
        self.db.commit()

    def mark_all_as_read(self, admin_id: uuid.UUID):
        self.db.query(Notification).filter(
            Notification.admin_id == admin_id,
            Notification.read == False,
        ).update({"read": True}, synchronize_session=False)
        self.db.commit()

    def get_admins_by_roles(self, roles: list[str]) -> list[Admin]:
        return self.db.query(Admin).filter(
            Admin.role.in_(roles),
            Admin.is_active == True,
        ).all()
