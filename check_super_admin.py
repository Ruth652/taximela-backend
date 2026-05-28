"""
Checks if ruthgashahun5@gmail.com is properly set up as super_admin in the DB.
If not, seeds it correctly using the real Firebase UID from the token.
"""
from dotenv import load_dotenv
load_dotenv()

# Import ALL models so SQLAlchemy can resolve all relationships
from infrastructure.database import SessionLocal
from domain.user_model import User
from domain.admin_model import Admin
from domain.auth_identity_model import AuthIdentity
from domain.contribution_model import Contribution
from domain.contribution_group_model import ContributionGroup
from domain.business_model import Business
from domain.business_registration_model import BusinessRegistration
from domain.gtfs_model import GTFS
import uuid

FIREBASE_UID = "zxpr2wzGN2RIiRVwMfk38reIBKG2"  # from the decoded token
EMAIL = "ruthgashahun5@gmail.com"
FULL_NAME = "Ruth"

db = SessionLocal()

try:
    # 1. Check auth_identity
    identity = db.query(AuthIdentity).filter(
        AuthIdentity.firebase_uid == FIREBASE_UID
    ).first()

    if identity:
        print(f"✅ auth_identity found: entity_id={identity.entity_id}, type={identity.entity_type}")
        user_id = identity.entity_id
    else:
        print("❌ No auth_identity found for this Firebase UID — creating...")
        # Check if user exists by email
        user = db.query(User).filter(User.email == EMAIL).first()
        if not user:
            print("   Creating user record...")
            user = User(
                id=uuid.uuid4(),
                email=EMAIL,
                full_name=FULL_NAME,
                status="active"
            )
            db.add(user)
            db.flush()

        identity = AuthIdentity(
            firebase_uid=FIREBASE_UID,
            entity_type="admin",
            entity_id=user.id
        )
        db.add(identity)
        db.flush()
        user_id = user.id
        print(f"   ✅ Created auth_identity for user_id={user_id}")

    # 2. Check user
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        print(f"✅ User found: {user.email}, id={user.id}")
    else:
        print("❌ User record missing")

    # 3. Check admin record
    admin = db.query(Admin).filter(
        Admin.user_id == user_id,
        Admin.is_active == True
    ).first()

    if admin:
        print(f"✅ Admin found: role={admin.role}, is_active={admin.is_active}, id={admin.id}")
    else:
        print("❌ No admin record found — creating super_admin...")
        admin = Admin(
            id=uuid.uuid4(),
            user_id=user_id,
            role="super_admin",
            is_active=True,
            created_by=None
        )
        db.add(admin)
        db.flush()
        print(f"   ✅ Created super_admin with id={admin.id}")

    db.commit()
    print("\n✅ Super admin is fully set up. Get a fresh token and try again.")

except Exception as e:
    db.rollback()
    print(f"\n❌ Error: {e}")
finally:
    db.close()
