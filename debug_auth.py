from dotenv import load_dotenv
load_dotenv()

from infrastructure.database import SessionLocal
from domain.user_model import User
from domain.admin_model import Admin
from domain.auth_identity_model import AuthIdentity, EntityTypeEnum
from domain.contribution_model import Contribution
from domain.contribution_group_model import ContributionGroup
from domain.business_model import Business
from domain.business_registration_model import BusinessRegistration
from domain.gtfs_model import GTFS

FIREBASE_UID = "zxpr2wzGN2RIiRVwMfk38reIBKG2"

db = SessionLocal()

try:
    # Step 1: auth_identity lookup
    identity = db.query(AuthIdentity).filter(
        AuthIdentity.firebase_uid == FIREBASE_UID
    ).first()
    print(f"1. auth_identity: {identity}")
    if identity:
        print(f"   entity_id={identity.entity_id}, entity_type={identity.entity_type!r}")

    if not identity:
        print("❌ No auth_identity found — stopping")
        exit()

    user_id = identity.entity_id

    # Step 2: check entity_type filter used in get_admin_uuids
    admin_uuids_str = db.query(AuthIdentity.entity_id).filter(
        AuthIdentity.entity_type == "admin"
    ).all()
    print(f"\n2. entity_type == 'admin' (string): {admin_uuids_str}")

    admin_uuids_enum = db.query(AuthIdentity.entity_id).filter(
        AuthIdentity.entity_type == EntityTypeEnum.admin
    ).all()
    print(f"   entity_type == EntityTypeEnum.admin: {admin_uuids_enum}")

    # Step 3: check admin record
    admin = db.query(Admin).filter(
        Admin.user_id == user_id
    ).first()
    print(f"\n3. Admin record: {admin}")
    if admin:
        print(f"   role={admin.role!r}, is_active={admin.is_active}, user_id={admin.user_id}")

    # Step 4: simulate get_super_admin_uuid_by_firebase_uid
    from repository.auth_identity_repository import AuthIdentityRepository
    repo = AuthIdentityRepository(db)
    result = repo.get_super_admin_uuid_by_firebase_uid([FIREBASE_UID])
    print(f"\n4. get_super_admin_uuid_by_firebase_uid result: {result}")

    if result:
        print("✅ Super admin lookup works — 403 must be a stale token issue")
    else:
        print("❌ Super admin lookup returns empty — this is the 403 cause")

finally:
    db.close()
