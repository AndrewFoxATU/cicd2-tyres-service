import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./test_tyres.db"
os.environ["JWT_SECRET"] = "test-secret-0123456789abcdef0123456789abcdef"

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app, get_db
from app.models import Base
from app.database import engine, SessionLocal
from app.auth import JWT_ALGORITHM, JWT_SECRET


def make_token(user_id, name, role):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id) if user_id is not None else name,
        "user_id": user_id,
        "name": name,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=30),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def client():
    """Client authenticated as an admin (most tests exercise CRUD)."""
    with _client() as c:
        c.headers.update({"Authorization": f"Bearer {make_token(1, 'admin', 'admin')}"})
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client():
    """Client with no Authorization header."""
    with _client() as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def employee_headers():
    return {"Authorization": f"Bearer {make_token(2, 'emp', 'employee')}"}


@pytest.fixture
def service_headers():
    return {"Authorization": f"Bearer {make_token(None, 'orders-service', 'service')}"}
