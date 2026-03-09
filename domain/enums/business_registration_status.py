from enum import Enum


class BusinessRegistrationStatus(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


class ApplicationAction(str, Enum):
    approve = "approve"
    reject = "reject"