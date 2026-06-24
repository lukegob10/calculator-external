from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.seed import seed_demo_data


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def override_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        seed_demo_data(db)
        db.commit()


def login(soeid: str = "lgoblirsch", password: str = "Demo123!") -> str:
    response = client.post("/api/auth/login", json={"soeid": soeid, "password": password})
    assert response.status_code == 200
    return response.json()["data"]["token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_pending_user_cannot_login():
    response = client.post("/api/auth/login", json={"soeid": "mchen", "password": "Demo123!"})
    assert response.status_code == 403


def test_business_user_create_run_share_and_revoke():
    owner_token = login()
    payload = {
        "name": "Test Calculation",
        "description": "Integration test",
        "asset": {"identifier": "CUSIP TEST", "identifier_type": "CUSIP", "name": "Test Asset", "asset_type": "External Asset"},
        "input_payload": {
            "asset_value": 84200000,
            "balance": 76000000,
            "price": 98.625,
            "spread_bps": 245,
            "rate_percent": 6.4,
            "capital_allocation": 11400000,
            "tax_jurisdiction": "DEFAULT",
        },
    }
    create_response = client.post("/api/calculations", json=payload, headers=auth(owner_token))
    assert create_response.status_code == 200
    calculation_id = create_response.json()["data"]["id"]

    run_response = client.post(f"/api/calculations/{calculation_id}/runs", headers=auth(owner_token))
    assert run_response.status_code == 200
    assert run_response.json()["data"]["result"]["external_return_percent"] != 0

    share_response = client.post(
        "/api/shares",
        json={"resource_id": calculation_id, "grantee_soeid": "apatel", "permission_level": "VIEW"},
        headers=auth(owner_token),
    )
    assert share_response.status_code == 200
    share_id = share_response.json()["data"]["id"]

    collaborator_token = login("apatel", "Demo123!")
    view_response = client.get(f"/api/calculations/{calculation_id}", headers=auth(collaborator_token))
    assert view_response.status_code == 200
    assert view_response.json()["data"]["permission"] == "VIEW"

    edit_response = client.patch(f"/api/calculations/{calculation_id}", json={"description": "blocked"}, headers=auth(collaborator_token))
    assert edit_response.status_code == 403

    revoke_response = client.delete(f"/api/shares/{share_id}", headers=auth(owner_token))
    assert revoke_response.status_code == 200

    blocked_response = client.get(f"/api/calculations/{calculation_id}", headers=auth(collaborator_token))
    assert blocked_response.status_code == 403


def test_admin_can_activate_pending_user_and_publish_parameter_set():
    admin_token = login("admin", "Admin123!")
    users = client.get("/api/admin/users", headers=auth(admin_token)).json()["data"]
    pending = next(user for user in users if user["soeid"] == "mchen")

    activate = client.patch(f"/api/admin/users/{pending['id']}", json={"status": "ACTIVE"}, headers=auth(admin_token))
    assert activate.status_code == 200
    assert activate.json()["data"]["status"] == "ACTIVE"

    create = client.post(
        "/api/admin/parameter-sets",
        json={"name": "Tax Methodology", "version": "v9.9-test", "effective_date": "2026-07-01", "payload": {"default_tax_rate": 0.2, "capital_charge_rate": 0.08}},
        headers=auth(admin_token),
    )
    assert create.status_code == 200
    parameter_id = create.json()["data"]["id"]
    publish = client.post(f"/api/admin/parameter-sets/{parameter_id}/publish", headers=auth(admin_token))
    assert publish.status_code == 200
    assert publish.json()["data"]["status"] == "PUBLISHED"


def test_admin_access_explorer_and_user_detail_are_admin_only():
    user_token = login()
    forbidden = client.get("/api/admin/access-grants", headers=auth(user_token))
    assert forbidden.status_code == 403

    admin_token = login("admin", "Admin123!")
    grants = client.get("/api/admin/access-grants", headers=auth(admin_token))
    assert grants.status_code == 200
    grant_data = grants.json()["data"]
    assert len(grant_data) >= 1
    assert {"calculation_name", "calculation_owner_name", "grantee_soeid", "permission_level"}.issubset(grant_data[0].keys())

    users = client.get("/api/admin/users", headers=auth(admin_token)).json()["data"]
    luke = next(user for user in users if user["soeid"] == "lgoblirsch")
    detail = client.get(f"/api/admin/users/{luke['id']}", headers=auth(admin_token))
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["user"]["soeid"] == "lgoblirsch"
    assert body["owned_calculations"] >= 1
