"""
NotificationService — creates notifications for all admins of the relevant roles.

Usage (from any usecase):
    from services.notification_service import NotificationService
    NotificationService(db).notify(
        event="contribution_new",
        message="Haile submitted a new station contribution",
        action_url="/dashboard/contributions"
    )
"""

from repository.notification_repository import NotificationRepository

# Maps each event type to its metadata and target roles
NOTIFICATION_CONFIG = {
    "contribution_new": {
        "title": "New contribution submitted",
        "priority": "medium",
        "roles": ["super_admin", "operational_admin"],
        "action_url": "/dashboard/contributions",
    },
    "contribution_approved": {
        "title": "Contribution approved",
        "priority": "low",
        "roles": ["super_admin", "operational_admin"],
        "action_url": "/dashboard/contributions",
    },
    "contribution_rejected": {
        "title": "Contribution rejected",
        "priority": "low",
        "roles": ["super_admin", "operational_admin"],
        "action_url": "/dashboard/contributions",
    },
    "business_application": {
        "title": "New business registration submitted",
        "priority": "medium",
        "roles": ["super_admin", "business_admin"],
        "action_url": "/dashboard/service-places",
    },
    "business_approved": {
        "title": "Business registration approved",
        "priority": "low",
        "roles": ["super_admin", "business_admin"],
        "action_url": "/dashboard/service-places",
    },
    "business_rejected": {
        "title": "Business registration rejected",
        "priority": "low",
        "roles": ["super_admin", "business_admin"],
        "action_url": "/dashboard/service-places",
    },
    "user_suspended": {
        "title": "User suspended",
        "priority": "high",
        "roles": ["super_admin", "operational_admin"],
        "action_url": "/dashboard/users",
    },
    "admin_added": {
        "title": "New admin added",
        "priority": "medium",
        "roles": ["super_admin"],
        "action_url": "/dashboard/admins",
    },
    "admin_removed": {
        "title": "Admin removed",
        "priority": "medium",
        "roles": ["super_admin"],
        "action_url": "/dashboard/admins",
    },
    "system_alert": {
        "title": "System alert",
        "priority": "critical",
        "roles": ["super_admin"],
        "action_url": None,
    },
}


class NotificationService:
    def __init__(self, db):
        self.db = db
        self.repo = NotificationRepository(db)

    def notify(self, event: str, message: str, action_url: str = None):
        """
        Creates a notification for every active admin whose role matches the event.

        Args:
            event:      One of the keys in NOTIFICATION_CONFIG (e.g. "contribution_new")
            message:    Human-readable description (e.g. "Haile submitted a new station")
            action_url: Optional override for the default action URL
        """
        config = NOTIFICATION_CONFIG.get(event)
        if not config:
            return  # Unknown event — silently skip

        target_roles = config["roles"]
        admins = self.repo.get_admins_by_roles(target_roles)

        for admin in admins:
            self.repo.create_notification(
                admin_id=admin.id,
                type=event,
                title=config["title"],
                message=message,
                priority=config["priority"],
                action_url=action_url or config["action_url"],
            )

        self.db.commit()
