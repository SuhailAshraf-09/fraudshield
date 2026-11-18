from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass
from uuid import uuid4
import json
import math

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed" / "test.csv"
REPORT = ROOT / "reports" / "phase8" / "ml_save_test.json"

BASE = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/ml/predict-and-save"

FEATURES = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

print("\nFRAUDSHIELD AI - ML PREDICT AND SAVE TEST")

if not DATA.is_file():
    raise SystemExit("Test dataset missing.")

df = pd.read_csv(DATA, nrows=100)

if "Class" not in df.columns:
    raise SystemExit("Dataset Class column missing.")

normal = df[df["Class"] == 0]

if normal.empty:
    raise SystemExit("No normal test transaction available.")

sample = normal.iloc[0]

features = {
    name: float(sample[name])
    for name in FEATURES
}

if not all(math.isfinite(v) for v in features.values()):
    raise SystemExit("Invalid feature values.")

test_id = "FSMLTEST" + uuid4().hex[:16]

payload = {
    "transaction_id": test_id,
    "amount_minor": max(
        0, round(float(sample["Amount"]) * 100)
    ),
    "currency": "USD",
    "occurred_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "features": features
}

# Currency and timestamp above are synthetic test metadata.
# They are not claims about the dataset's source transactions.

REPORT.parent.mkdir(parents=True, exist_ok=True)

results = {
    "test_transaction_id": test_id,
    "test_type": "synthetic normal transaction",
    "saved_to_database": False
}

# Save the unique ID before any write request.
REPORT.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

with httpx.Client(timeout=60) as client:

    schema = client.get(BASE + "/openapi.json")
    schema.raise_for_status()

    operation = schema.json()["paths"][ENDPOINT]["post"]

    if not operation.get("security"):
        raise SystemExit(
            "SAFETY STOP: JWT protection not declared."
        )

    print("New ML API: VERIFIED")
    print("JWT Security: DECLARED")

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
        raise SystemExit("Admin login failed.")

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    unauthorized = client.post(
        BASE + ENDPOINT,
        json=payload
    )

    print(
        "Unauthorized Status:",
        unauthorized.status_code
    )

    if unauthorized.status_code != 401:
        raise SystemExit(
            "SAFETY STOP: Unauthorized access check failed."
        )

    invalid_payload = {
        **payload,
        "features": {
            key: value
            for key, value in features.items()
            if key != "V28"
        }
    }

    invalid = client.post(
        BASE + ENDPOINT,
        headers=headers,
        json=invalid_payload
    )

    print(
        "Invalid Features Status:",
        invalid.status_code
    )

    if invalid.status_code != 422:
        raise SystemExit(
            "SAFETY STOP: Feature validation failed."
        )

    print("\nSubmitting one authorized ML prediction...")

    valid = client.post(
        BASE + ENDPOINT,
        headers=headers,
        json=payload
    )

    results["prediction_status"] = valid.status_code
    results["unauthorized_status"] = unauthorized.status_code
    results["invalid_features_status"] = invalid.status_code

    print("Prediction API Status:", valid.status_code)

    if valid.status_code in (200, 201):
        body = valid.json()

        for field in (
            "prediction_id",
            "model_version",
            "model_score",
            "threshold",
            "classification",
            "risk_tier",
            "requires_review",
            "saved_to_database"
        ):
            results[field] = body.get(field)
            print(field + ":", body.get(field))

        results["checks_passed"] = (
            body.get("saved_to_database") is True
            and body.get("transaction_id") == test_id
            and body.get("model_version") == "random-forest-v1"
        )

    else:
        results["checks_passed"] = False
        print("API Error Response:", valid.text[:600])

REPORT.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nReport saved:", REPORT)
print("checks_passed:", results["checks_passed"])

if not results["checks_passed"]:
    raise SystemExit(
        "ML integration needs review. Do not rerun yet."
    )

print("\nML PREDICT AND SAVE API TEST PASSED!")
print("PostgreSQL record verification: NEXT STEP")
