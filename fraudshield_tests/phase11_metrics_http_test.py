import json
from pathlib import Path
from getpass import getpass

import httpx

BASE = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/ml/model/metrics"

print("\nFRAUDSHIELD AI - PHASE 11 STEP 11L")

email = input("Admin email: ").strip()
password = getpass("Admin password: ")

with httpx.Client(base_url=BASE, timeout=20) as client:

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )

    del password

    print("ADMIN LOGIN:", login.status_code)

    if login.status_code != 200:
        raise SystemExit("Authentication failed.")

    token = login.json()["access_token"]

    response = client.get(
        ENDPOINT,
        headers={"Authorization": f"Bearer {token}"}
    )

    print("ML METRICS HTTP:", response.status_code)

    if response.status_code != 200:
        raise SystemExit("ML metrics API test failed.")

    metrics = response.json()

expected = json.loads(
    Path("ml_models/random_forest_v1_metrics.json")
    .read_text(encoding="utf-8")
)

keys = (
    "model_version",
    "test_records",
    "precision",
    "recall",
    "f1_score",
    "average_precision",
    "production_ready"
)

for key in keys:
    if metrics.get(key) != expected.get(key):
        raise SystemExit(
            f"METADATA MISMATCH: {key}"
        )

print("MODEL:", metrics["model_version"])
print("TEST RECORDS:", metrics["test_records"])
print("PRECISION:", round(metrics["precision"] * 100, 2), "%")
print("RECALL:", round(metrics["recall"] * 100, 2), "%")
print("F1 SCORE:", round(metrics["f1_score"] * 100, 2), "%")
print("PR-AUC:", round(metrics["average_precision"] * 100, 2), "%")
print("PRODUCTION READY:", metrics["production_ready"])

print("\nAUTHENTICATED ML METRICS API: PASSED")
print("DATABASE WRITES: NONE")
