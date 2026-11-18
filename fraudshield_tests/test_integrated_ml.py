from pathlib import Path
from getpass import getpass
import json
import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8000/api/v1"

DATA = ROOT / "data" / "processed" / "test.csv"
REPORT = ROOT / "reports" / "phase4" / "jwt_ml_integration.json"

FEATURES = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

if not DATA.is_file():
    raise SystemExit("Test dataset not found.")

# Select two example transactions
df = pd.read_csv(DATA)

normal = df[df["Class"] == 0].head(1)
fraud = df[df["Class"] == 1].head(1)

if normal.empty or fraud.empty:
    raise SystemExit("Test samples missing.")

samples = pd.concat([normal, fraud])

email = input("Admin email: ").strip()
password = getpass("Admin password: ")

results = {}

with httpx.Client(timeout=30) as client:

    # Authenticate with the existing FastAPI backend
    login = client.post(
        BASE + "/auth/login",
        json={"email": email, "password": password}
    )

    del password

    results["login_status"] = login.status_code

    if login.status_code != 200:
        raise SystemExit(
            f"Login failed: HTTP {login.status_code}"
        )

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    profile = client.get(
        BASE + "/auth/me",
        headers=headers
    )

    results["profile_status"] = profile.status_code

    for index, (_, row) in enumerate(samples.iterrows()):

        payload = {
            "features": {
                name: float(row[name])
                for name in FEATURES
            }
        }

        if index == 0:
            # Verify prediction without authorization
            unauthorized = client.post(
                BASE + "/ml/predict",
                json=payload
            )

            results["unauthorized_status"] = (
                unauthorized.status_code
            )

            # Verify missing features are rejected
            invalid_payload = {
                "features": payload["features"].copy()
            }
            del invalid_payload["features"]["Amount"]

            invalid = client.post(
                BASE + "/ml/predict",
                json=invalid_payload,
                headers=headers
            )

            results["invalid_input_status"] = (
                invalid.status_code
            )

        # Send authorized transaction for ML inference
        response = client.post(
            BASE + "/ml/predict",
            json=payload,
            headers=headers
        )

        label = "normal" if index == 0 else "fraud"

        results[f"{label}_prediction_status"] = (
            response.status_code
        )

        if response.status_code == 200:
            output = response.json()

            results[f"{label}_prediction"] = {
                "actual_class": int(row["Class"]),
                "classification": output.get("classification"),
                "model_score": output.get("model_score"),
                "model_version": output.get("model_version")
            }
        else:
            print(
                f"{label} prediction failed:",
                response.status_code,
                response.text[:300]
            )

results["checks_passed"] = all([
    results.get("login_status") == 200,
    results.get("profile_status") == 200,
    results.get("unauthorized_status") == 401,
    results.get("invalid_input_status") == 422,
    results.get("normal_prediction_status") == 200,
    results.get("fraud_prediction_status") == 200
])

REPORT.parent.mkdir(parents=True, exist_ok=True)

REPORT.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFRAUDSHIELD AI - INTEGRATED ML TEST")

for key, value in results.items():
    print(f"{key}: {value}")

print("\nReport saved:", REPORT)

if not results["checks_passed"]:
    raise SystemExit("Some integration tests failed.")

print("\nJWT + ML integration testing successful!")
