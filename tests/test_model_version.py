from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import Prediction
from app.security import reviewer_or_admin
from app.ml_persistence_router import router


def test_saved_random_forest_model_version():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/v1/ml")

    def override_db():
        with TestSession() as db:
            yield db

    test_app.dependency_overrides[get_db] = override_db
    test_app.dependency_overrides[reviewer_or_admin] = lambda: None

    features = {"Time": 0.0, "Amount": 12.0}
    features.update({
        f"V{i}": 0.0 for i in range(1, 29)
    })

    payload = {
        "transaction_id": "PHASE13_REGRESSION",
        "amount_minor": 1200,
        "currency": "INR",
        "occurred_at": "2026-11-19T12:00:00+00:00",
        "features": features
    }

    try:
        with TestClient(test_app) as client:
            response = client.post(
                "/api/v1/ml/predict-and-save",
                json=payload
            )

        assert response.status_code == 200, response.text

        with TestSession() as db:
            prediction = db.scalar(select(Prediction))
            assert prediction is not None
            assert prediction.model_version == "random-forest-v1"
    finally:
        test_app.dependency_overrides.clear()
        engine.dispose()
