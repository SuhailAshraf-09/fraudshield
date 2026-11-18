from pathlib import Path
import json
import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8001/api/v1/ml"

KEY = (ROOT / ".ml_api_key").read_text().strip()
TEST = ROOT / "data" / "processed" / "test.csv"
REPORT = ROOT / "reports" / "phase4" / "ml_api_test.json"

features = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

df = pd.read_csv(TEST, nrows=1)

payload = {
    "features": {
        name: float(df.iloc[0][name])
        for name in features
    }
}

headers = {"X-ML-API-Key": KEY}

with httpx.Client(timeout=30) as client:
    health = client.get(BASE + "/health")

    unauthorized = client.post(
        BASE + "/predict", json=payload
    )

    authorized = client.post(
        BASE + "/predict",
        json=payload,
        headers=headers
    )

    invalid_payload = {
        "features": payload["features"].copy()
    }
    del invalid_payload["features"]["Amount"]

    invalid = client.post(
        BASE + "/predict",
        json=invalid_payload,
        headers=headers
    )

results = {
    "health_status": health.status_code,
    "unauthorized_status": unauthorized.status_code,
    "prediction_status": authorized.status_code,
    "invalid_input_status": invalid.status_code,
}

results["checks_passed"] = (
    health.status_code == 200
    and unauthorized.status_code == 401
    and authorized.status_code == 200
    and invalid.status_code == 422
)

if authorized.status_code == 200:
    results["prediction"] = authorized.json()

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(results, indent=2))

print("\nFRAUDSHIELD AI - ML API RESULTS")

for key, value in results.items():
    print(key, ":", value)
