import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base

TEST_DATABASE_URL = "sqlite:///./test_tyres.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

VALID_PAYLOAD = {
    "brand": "TestBrand",
    "model": "TestModel",
    "size": "205/55R16",
    "load_rate": 91,
    "speed_rate": "H",
    "season": "Summer",
    "supplier": "TestSupplier",
    "fuel_efficiency": "C",
    "noise_level": 70,
    "weather_efficiency": "C",
    "ev_approved": False,
    "cost": "100.00",
    "quantity": 10
}

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_tyre():
    response = client.post("/api/tyres", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert Decimal(str(data["retail_cost"])) == Decimal("135.00")

def test_list_tyres():
    client.post("/api/tyres", json=VALID_PAYLOAD)
    response = client.get("/api/tyres")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_tyre_by_id():
    created = client.post("/api/tyres", json=VALID_PAYLOAD).json()
    response = client.get(f"/api/tyres/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]

def test_get_tyre_404():
    response = client.get("/api/tyres/99999")
    assert response.status_code == 404

def test_update_tyre():
    created = client.post("/api/tyres", json=VALID_PAYLOAD).json()
    updated_payload = VALID_PAYLOAD.copy()
    updated_payload["cost"] = "200.00"
    updated_payload["brand"] = "Brand2"
    updated_payload["model"] = "Model2"

    response = client.put(f"/api/tyres/{created['id']}", json=updated_payload)
    assert response.status_code == 200
    assert Decimal(str(response.json()["retail_cost"])) == Decimal("270.00")

def test_patch_tyre():
    created = client.post("/api/tyres", json=VALID_PAYLOAD).json()
    response = client.patch(
        f"/api/tyres/{created['id']}",
        json={"cost": "150.00"}
    )
    assert response.status_code == 200
    assert Decimal(str(response.json()["retail_cost"])) == Decimal("202.50")

def test_delete_tyre():
    created = client.post("/api/tyres", json=VALID_PAYLOAD).json()
    response = client.delete(f"/api/tyres/{created['id']}")
    assert response.status_code == 204

    followup = client.get(f"/api/tyres/{created['id']}")
    assert followup.status_code == 404


# Failing tests

def test_create_tyre_invalid_speed_rate():
    bad = VALID_PAYLOAD.copy()
    bad["speed_rate"] = "Z"
    response = client.post("/api/tyres", json=bad)
    assert response.status_code == 422

def test_negative_cost():
    bad = VALID_PAYLOAD.copy()
    bad["cost"] = "-10.00"
    response = client.post("/api/tyres", json=bad)
    assert response.status_code == 422

def test_missing_required_field():
    bad = VALID_PAYLOAD.copy()
    del bad["brand"]
    response = client.post("/api/tyres", json=bad)
    assert response.status_code == 422

def test_patch_invalid_speed_rate():
    created = client.post("/api/tyres", json=VALID_PAYLOAD).json()
    response = client.patch(
        f"/api/tyres/{created['id']}",
        json={"speed_rate": "INVALID"}
    )
    assert response.status_code == 422
