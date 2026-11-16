import os
import secrets
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = secrets.token_urlsafe(40)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionTest = sessionmaker(engine, expire_on_commit=False)

@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionTest() as db:
        db.add(User(email="admin@example.test", role="admin", password_hash=hash_password("SufficientlyStrongPassword123!")))
        db.commit()

    def test_db():
        with SessionTest() as db:
            yield db
    app.dependency_overrides[get_db] = test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def auth(client):
    resp = client.post("/api/v1/auth/login", json={"email": "admin@example.test", "password": "SufficientlyStrongPassword123!"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


def sample():
    return {"transaction_id": "DEMO_001", "amount_minor": 500000, "currency": "INR",
            "occurred_at": "2026-11-14T10:30:00+05:30",
            "features": {"new_device": True, "international": True, "tx_24h": 10,
                         "distance_km": 850, "hour": 2}}


def test_health_and_protection(client):
    assert client.get("/api/v1/health/live").status_code == 200
    assert client.get("/api/v1/dashboard/summary").status_code == 401
    assert client.get("/api/v1/health/ready").status_code == 200


def test_prediction_alert_and_idempotency(client):
    headers = auth(client)
    resp = client.post("/api/v1/predictions", json=sample(), headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["risk_tier"] == "HIGH"
    assert data["risk_probability"] is None
    assert data["demo_only"] is True
    assert client.post("/api/v1/predictions", json=sample(), headers=headers).json()["prediction_id"] == data["prediction_id"]
    summary = client.get("/api/v1/dashboard/summary", headers=headers).json()
    assert summary["total_transactions"] == 1
    assert summary["flagged_transactions"] == 1
    alert = client.get("/api/v1/alerts", headers=headers).json()[0]
    assert client.patch("/api/v1/alerts/" + alert["id"], json={"status": "in_review", "notes": "Demo review"}, headers=headers).status_code == 200
    assert client.get("/api/v1/analytics/trends", headers=headers).status_code == 200


def test_changed_duplicate_rejected(client):
    headers = auth(client)
    client.post("/api/v1/predictions", json=sample(), headers=headers)
    changed = sample()
    changed["amount_minor"] = 900000
    assert client.post("/api/v1/predictions", json=changed, headers=headers).status_code == 409


def test_bad_payload_rejected(client):
    headers = auth(client)
    changed = sample()
    changed["currency"] = "INR123"
    assert client.post("/api/v1/predictions", json=changed, headers=headers).status_code == 422
