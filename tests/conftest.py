"""
Pytest configuration for TaxiMela backend tests.
"""
import sys
import os
import uuid
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["ENV"] = "testing"
os.environ["OTP_BASE_URL"] = "http://mock-otp:8080/otp/routers/default/index/graphql"

# ============================================================
# 1. Mock Firebase
# ============================================================
import firebase_admin
mock_app = MagicMock()
mock_app.name = "test-firebase-app"
firebase_admin._apps["test_mock_app"] = mock_app
patch('firebase_admin.credentials.Certificate', return_value=MagicMock()).start()

# ============================================================
# 2. Mock SQLAlchemy create_engine (SQLite in-memory)
# ============================================================
from sqlalchemy import create_engine as real_create_engine
from sqlalchemy.pool import StaticPool

def mock_create_engine(url, **kwargs):
    return real_create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

patch('sqlalchemy.create_engine', side_effect=mock_create_engine).start()

# ============================================================
# 3. Patch OTP service to return fake data for all tests
# ============================================================
async def mock_fetch_route_from_otp(*args, **kwargs):
    """Return a valid OTP response without calling external service."""
    return {
        "data": {
            "plan": {
                "itineraries": [
                    {
                        "duration": 1800,
                        "walkDistance": 300.0,
                        "numberOfTransfers": 0,
                        "legs": [
                            {
                                "mode": "BUS",
                                "startTime": 1640000000000,
                                "endTime": 1640001800000,
                                "from": {
                                    "name": "Saris Terminal",
                                    "lat": 9.0104,
                                    "lon": 38.7613
                                },
                                "to": {
                                    "name": "Megenagna Terminal",
                                    "lat": 9.0192,
                                    "lon": 38.7521
                                },
                                "route": {
                                    "shortName": "1042",
                                    "longName": "Saris - Megenagna"
                                },
                                "distance": 4200.0,
                                "legGeometry": {
                                    "points": "mock_polyline",
                                    "length": 4200
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }

patch('infrastructure.route_services.fetch_route_from_otp', 
      side_effect=mock_fetch_route_from_otp).start()

# ============================================================
# 4. Import db_module and patch create_all (JSONB -> JSON)
# ============================================================
import infrastructure.database as db_module
from sqlalchemy import JSON

_original_create_all = db_module.Base.metadata.create_all

def _safe_create_all(bind=None, **kwargs):
    for table in db_module.Base.metadata.tables.values():
        for col in list(table.columns):
            if str(col.type).upper() == 'JSONB':
                col.type = JSON()
    try:
        _original_create_all(bind=bind, **kwargs)
    except Exception as e:
        print(f"[conftest] create_all error: {e}")

db_module.Base.metadata.create_all = _safe_create_all

# ============================================================
# 5. Import app, create tables, seed DB
# ============================================================
from delivery.main import app
from infrastructure.database import SessionLocal

db_module.Base.metadata.create_all(bind=db_module.engine)

from domain.auth_identity_model import AuthIdentity

test_entity_id = uuid.uuid4()
test_firebase_uid = "test-uid-123"

session = SessionLocal()
try:
    existing = session.query(AuthIdentity).filter_by(firebase_uid=test_firebase_uid).first()
    if not existing:
        session.add(AuthIdentity(
            firebase_uid=test_firebase_uid,
            entity_type="user",
            entity_id=test_entity_id
        ))
        session.commit()
except Exception as e:
    session.rollback()
    print(f"[conftest] Seed error (may be ok): {e}")
finally:
    session.close()

# ============================================================
# 6. Pytest fixtures
# ============================================================
import pytest

@pytest.fixture(scope="session", autouse=True)
def mock_firebase_auth():
    with patch('firebase_admin.auth.verify_id_token') as mock_verify:
        mock_verify.return_value = {
            "uid": test_firebase_uid,
            "email": "test@test.com"
        }
        yield mock_verify
