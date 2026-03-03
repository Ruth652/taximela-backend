from domain.user_model import User
from domain.auth_identity_model import AuthIdentity
from domain.contribution_model import Contribution
from sqlalchemy.orm import relationship

from .user_model import User
from .auth_identity_model import AuthIdentity
from .contribution_model import Contribution

from .business_model import Business
from .business_registration_model import BusinessRegistration
from .business_category_model import BusinessCategory
from .admin_model import Admin

# User.contributions = relationship(
#     "Contribution", 
#     back_populates="user", 
#     primaryjoin="User.id == Contribution.user_id")

# Contribution.user = relationship(
#     "User",
#     back_populates="contributions",
#     primaryjoin="Contribution.user_id == User.id"
# )
