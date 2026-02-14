from infrastructure.database import SessionLocal, Base, engine
from domain.user_model import User
from domain.admin_model import Admin
from domain.auth_identity_model import AuthIdentity
import uuid

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create test user
test_user = User(
    id=uuid.uuid4(),
    email="admin@test.com",
    full_name="Test Admin",
    status="active"
)
db.add(test_user)
db.commit()

# Link to Firebase UID
auth_identity = AuthIdentity(
    firebase_uid="test-admin-uid",
    entity_type="user",
    entity_id=test_user.id
)
db.add(auth_identity)
db.commit()

# Make user a super admin
admin = Admin(
    user_id=test_user.id,
    role="super_admin",
    is_active=True
)
db.add(admin)
db.commit()

print(f"✅ Test admin created!")
print(f"User ID: {test_user.id}")
print(f"Email: {test_user.email}")
print(f"Firebase UID: test-admin-uid")

db.close()
