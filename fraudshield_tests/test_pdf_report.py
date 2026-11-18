from pathlib import Path
from getpass import getpass
import io
import json

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed" / "test.csv"
OUTPUT = ROOT / "reports" / "phase6"
OUTPUT.mkdir(parents=True, exist_ok=True)

BASE = "http://127.0.0.1:8000/api/v1"
FEATURES = ["Time", "Amount"] + [
    f"V{i}" for i in range(1, 29)
]

print("\nFRAUDSHIELD AI - PDF REPORT TEST")

df = pd.read_csv(DATA)

normal = df[df["Class"] == 0].head(1)
fraud = df[df["Class"] == 1].head(1)

sample = pd.concat(
    [normal, fraud],
    ignore_index=True
)

csv_data = sample[FEATURES].to_csv(
    index=False
).encode("utf-8")

email = input("Admin email: ").strip()
password = getpass("Admin password: ")

with httpx.Client(timeout=60) as client:
    login = client.post(
        BASE + "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    del password

    print("login_status:", login.status_code)

    if login.status_code != 200:
        raise SystemExit("Admin login failed.")

    token = login.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    unauthorized = client.post(
        BASE + "/ml/report-pdf",
        files={
            "file": (
                "sample.csv",
                csv_data,
                "text/csv"
            )
        }
    )

    report = client.post(
        BASE + "/ml/report-pdf",
        headers=headers,
        files={
            "file": (
                "sample.csv",
                csv_data,
                "text/csv"
            )
        }
    )

    invalid = client.post(
        BASE + "/ml/report-pdf",
        headers=headers,
        files={
            "file": (
                "invalid.csv",
                b"wrong,column\n1,2",
                "text/csv"
            )
        }
    )

pdf_valid = (
    report.status_code == 200
    and report.content.startswith(b"%PDF-")
    and "application/pdf" in report.headers.get(
        "content-type", ""
    )
)

results = {
    "unauthorized_status": unauthorized.status_code,
    "pdf_report_status": report.status_code,
    "invalid_schema_status": invalid.status_code,
    "valid_pdf_generated": pdf_valid
}

results["checks_passed"] = (
    unauthorized.status_code == 401
    and report.status_code == 200
    and invalid.status_code == 422
    and pdf_valid
)

if pdf_valid:
    pdf_path = OUTPUT / "fraud_investigation_sample.pdf"
    pdf_path.write_bytes(report.content)
    print("PDF saved:", pdf_path)

test_path = OUTPUT / "pdf_report_test.json"
test_path.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

for key, value in results.items():
    print(f"{key}: {value}")

if not results["checks_passed"]:
    raise SystemExit("PDF report testing failed.")

print("PDF REPORT TESTS PASSED!")
