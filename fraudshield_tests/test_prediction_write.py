from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass
from uuid import uuid4
import json

import httpx

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

print("\nFRAUDSHIELD AI - PREDICTION WRITE TEST")

BASE = "http://127.0.0.1:8000"
API = "/api/v1/predictions"

# Unique marker prevents collision with existing records.
test_id = "FSTEST" + uuid4().hex[:12]

payload = {
    "transaction_id": test_id,
    "amount_minor": 2500,
    "currency": "INR",
    "occurred_at": datetime.now(
        timezone.utc
    ).isoformat()
}

with httpx.Client(timeout=30) as client:
    schema_response = client.get(BASE + "/openapi.json")
    schema_response.raise_for_status()

    spec = schema_response.json()

    operation = spec["paths"][API]["post"]
    request_schema = spec["components"]["schemas"][
        "PredictionRequest"
    ]

    required = set(request_schema.get("required", []))
    properties = request_schema.get("properties", {})

    if not required.issubset(payload):
        raise SystemExit(
            "SAFETY STOP: Additional required API fields."
        )

    for name in payload:
        if name not in properties:
            raise SystemExit(
                f"SAFETY STOP: Unexpected field: {name}"
            )

    if not operation.get("security"):
        raise SystemExit(
            "SAFETY STOP: JWT security not declared."
        )

print("API schema validation: PASS")
print("JWT declaration: PASS")

db_password = getpass("PostgreSQL app password: ")

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="fraudshield_app",
        password=db_password,
        host="127.0.0.1",
        port=5432,
        database="fraudshield_db"
    ),
    poolclass=NullPool,
    hide_parameters=True,
    connect_args={"connect_timeout": 10}
)

del db_password

def counts():
    with engine.connect() as conn:
        identity = conn.execute(
            text(
                "SELECT current_database(), current_user"
            )
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong PostgreSQL target")

        return {
            table: conn.execute(
                text(f"SELECT COUNT(*) FROM public.{table}")
            ).scalar_one()
            for table in (
                "transactions",
                "predictions",
                "alerts"
            )
        }

try:
    before = counts()
    print("\nBEFORE API REQUEST:", before)

    email = input("Website admin email: ").strip()
    password = getpass("Website admin password: ")

    with httpx.Client(timeout=30) as client:
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
            raise SystemExit("Website admin login failed.")

        unauthorized = client.post(
            BASE + API,
            json=payload
        )

        print(
            "Unauthorized Status:",
            unauthorized.status_code
        )

        if unauthorized.status_code != 401:
            raise SystemExit(
                "SAFETY STOP: JWT protection check failed."
            )

        # Check that unauthorized request wrote nothing.
        if counts() != before:
            raise SystemExit(
                "SAFETY STOP: Data changed unexpectedly."
            )

        token = login.json()["access_token"]

        authorized = client.post(
            BASE + API,
            headers={
                "Authorization": f"Bearer {token}"
            },
            json=payload
        )

    print(
        "Prediction API Status:",
        authorized.status_code
    )

    if authorized.status_code not in (200, 201):
        print(
            "Validation/Error Response:",
            authorized.text[:1000]
        )
        raise SystemExit(
            "Prediction API request failed. Do not retry."
        )

    after = counts()
    print("AFTER API REQUEST:", after)

    differences = {
        name: after[name] - before[name]
        for name in before
    }

    print("RECORD DIFFERENCES:", differences)

    passed = (
        differences["transactions"] == 1
        and differences["predictions"] == 1
        and differences["alerts"] in (0, 1)
    )

    report = {
        "test_transaction_id": test_id,
        "login_status": login.status_code,
        "unauthorized_status": unauthorized.status_code,
        "prediction_status": authorized.status_code,
        "before": before,
        "after": after,
        "record_differences": differences,
        "checks_passed": passed,
        "test_records_retained": True
    }

    output = Path(
        "reports/phase7/prediction_write_test.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print("\nchecks_passed:", passed)
    print("Report saved:", output)

    if not passed:
        raise SystemExit(
            "Persistence results need review."
        )

    print("\nPREDICTION DATABASE WRITE TEST PASSED!")

finally:
    engine.dispose()
