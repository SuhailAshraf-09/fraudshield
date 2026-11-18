import json
from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass
from uuid import uuid4, uuid5, NAMESPACE_URL

import httpx
import pandas as pd

from app.ml_integrated_router import FEATURES, load_model

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data" / "processed" / "test.csv"
REPORT = ROOT / "reports" / "phase8" / "high_risk_alert_test.json"

BASE = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/ml/predict-and-save"

print("\nFRAUDSHIELD AI - HIGH RISK FRAUD ALERT TEST")

if not DATA.is_file():
    raise SystemExit("SAFETY STOP: Test dataset missing.")

if REPORT.exists():
    raise SystemExit(
        "SAFETY STOP: Previous high-risk report exists. "
        "Do not repeat this write test."
    )

df = pd.read_csv(DATA)

if "Class" not in df.columns:
    raise SystemExit("Dataset Class field missing.")

fraud = df.loc[df["Class"] == 1].copy()

if fraud.empty:
    raise SystemExit("No labelled fraud samples found.")

model, threshold = load_model()

scores = model.predict_proba(
    fraud[FEATURES]
)[:, 1]

best_index = max(
    range(len(scores)),
    key=lambda i: float(scores[i])
)

sample = fraud.iloc[best_index]
expected_score = float(scores[best_index])

print("Model:", "random-forest-v1")
print("Classification Threshold:", threshold)
print("Selected Sample Score:", round(expected_score, 6))

if expected_score < threshold:
    raise SystemExit(
        "SAFETY STOP: No selected sample exceeds threshold."
    )

test_id = "FSFRAUDTEST" + uuid4().hex[:16]

internal_id = str(uuid5(
    NAMESPACE_URL,
    "fraudshield-ai/ml/predict-and-save:" + test_id
))

payload = {
    "transaction_id": test_id,
    "amount_minor": max(
        0, round(float(sample["Amount"]) * 100)
    ),
    "currency": "USD",
    "occurred_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "features": {
        name: float(sample[name])
        for name in FEATURES
    }
}

# Currency and timestamp are synthetic test metadata.

REPORT.parent.mkdir(parents=True, exist_ok=True)

result = {
    "test_transaction_id": test_id,
    "internal_transaction_id": internal_id,
    "test_type": "labelled fraud sample",
    "expected_model_score": expected_score,
    "threshold": float(threshold),
    "status": "pending",
    "checks_passed": False
}

with REPORT.open("x", encoding="utf-8") as file:
    json.dump(result, file, indent=2)

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

try:
    with httpx.Client(timeout=60) as client:
        login = client.post(
            BASE + "/api/v1/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

        del password

        print("Login Status:", login.status_code)

        if login.status_code != 200:
            raise RuntimeError("Admin login failed.")

        unauthorized = client.post(
            BASE + ENDPOINT,
            json=payload
        )

        print(
            "Unauthorized Status:",
            unauthorized.status_code
        )

        if unauthorized.status_code != 401:
            raise RuntimeError(
                "JWT security check failed."
            )

        token = login.json()["access_token"]

        print("\nSubmitting high-risk fraud sample...")

        response = client.post(
            BASE + ENDPOINT,
            headers={
                "Authorization": f"Bearer {token}"
            },
            json=payload
        )

    print("Prediction API Status:", response.status_code)

    result["prediction_status"] = response.status_code

    if response.status_code == 200:
        body = response.json()

        for name in (
            "prediction_id",
            "model_version",
            "model_score",
            "classification",
            "risk_tier",
            "requires_review",
            "saved_to_database"
        ):
            result[name] = body.get(name)
            print(name + ":", body.get(name))

        result["checks_passed"] = (
            body.get("transaction_id") == test_id
            and body.get("model_version") == "random-forest-v1"
            and body.get("classification") == "FLAGGED"
            and body.get("risk_tier") == "HIGH"
            and body.get("requires_review") is True
            and body.get("saved_to_database") is True
            and abs(
                float(body.get("model_score", -1))
                - expected_score
            ) < 0.000002
        )

    else:
        print("API Error:", response.text[:400])

    result["status"] = (
        "api_passed" if result["checks_passed"]
        else "review_required"
    )

finally:
    REPORT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

print("\nchecks_passed:", result["checks_passed"])
print("Report:", REPORT)

if not result["checks_passed"]:
    raise SystemExit(
        "High-risk integration needs review. Do not rerun."
    )

print("\nHIGH-RISK FRAUD API TEST PASSED!")
print("PostgreSQL alert verification: NEXT STEP")
