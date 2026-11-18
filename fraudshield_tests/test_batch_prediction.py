from pathlib import Path
from getpass import getpass
import json

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed" / "test.csv"
REPORT = ROOT / "reports" / "phase5" / "batch_test.json"

BASE = "http://127.0.0.1:8000/api/v1"
FEATURES = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

print("\nFRAUDSHIELD AI - BATCH PREDICTION TEST")

df = pd.read_csv(DATA, nrows=3)

if len(df) != 3:
    raise SystemExit("Three sample records required.")

csv_data = df[FEATURES].to_csv(
    index=False
).encode("utf-8")

email = input("Admin email: ").strip()
password = getpass("Admin password: ")

with httpx.Client(timeout=60) as client:
    login = client.post(
        BASE + "/auth/login",
        json={"email": email, "password": password}
    )

    del password

    print("login_status:", login.status_code)

    if login.status_code != 200:
        raise SystemExit("Admin login failed.")

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    unauthorized = client.post(
        BASE + "/ml/batch-predict",
        files={
            "file": ("test.csv", csv_data, "text/csv")
        }
    )

    valid = client.post(
        BASE + "/ml/batch-predict",
        headers=headers,
        files={
            "file": ("test.csv", csv_data, "text/csv")
        }
    )

    invalid = client.post(
        BASE + "/ml/batch-predict",
        headers=headers,
        files={
            "file": (
                "invalid.csv",
                b"wrong,column\n1,2\n",
                "text/csv"
            )
        }
    )

results = {
    "login_status": login.status_code,
    "unauthorized_status": unauthorized.status_code,
    "batch_prediction_status": valid.status_code,
    "invalid_schema_status": invalid.status_code
}

if valid.status_code == 200:
    body = valid.json()
    results["total_transactions"] = body.get(
        "total_transactions"
    )
    results["flagged_transactions"] = body.get(
        "flagged_transactions"
    )
    results["model_version"] = body.get(
        "model_version"
    )

results["checks_passed"] = (
    login.status_code == 200
    and unauthorized.status_code == 401
    and valid.status_code == 200
    and invalid.status_code == 422
    and results.get("total_transactions") == 3
)

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

for key, value in results.items():
    print(f"{key}: {value}")

if not results["checks_passed"]:
    raise SystemExit("Batch prediction test failed.")

print("\nBatch prediction testing successful!")
