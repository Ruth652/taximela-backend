from domain.user_model import User
from domain.auth_identity_model import AuthIdentity
from domain.contribution_model import Contribution
from sqlalchemy.orm import relationship

User.contributions = relationship(
    "Contribution", 
    back_populates="user", 
    primaryjoin="User.id == Contribution.user_id")

Contribution.user = relationship(
    "User",
    back_populates="contributions",
    primaryjoin="Contribution.user_id == User.id"
)
