from pathlib import Path
from getpass import getpass
from datetime import datetime
from uuid import uuid5, NAMESPACE_URL
import json
import re
import shutil

import httpx
import psycopg

ROOT = Path(__file__).resolve().parent.parent

REPORT = (
    ROOT / "reports" / "phase8"
    / "high_risk_alert_test.json"
)

print("\nFRAUDSHIELD AI - HIGH RISK RECOVERY")

if not REPORT.is_file():
    raise SystemExit("SAFETY STOP: Pending report missing.")

data = json.loads(
    REPORT.read_text(encoding="utf-8")
)

test_id = data.get("test_transaction_id", "")

if not re.fullmatch(r"FSFRAUDTEST[0-9a-f]{16}", test_id):
    raise SystemExit("SAFETY STOP: Invalid test ID.")

if data.get("status") != "pending":
    raise SystemExit("SAFETY STOP: Report not pending.")

if data.get("checks_passed") is not False:
    raise SystemExit("SAFETY STOP: Unexpected test state.")

internal_id = str(uuid5(
    NAMESPACE_URL,
    "fraudshield-ai/ml/predict-and-save:" + test_id
))

if data.get("internal_transaction_id") != internal_id:
    raise SystemExit("SAFETY STOP: ID mismatch.")

print("Pending test report: VERIFIED")

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

try:
    response = httpx.post(
        "http://127.0.0.1:8000/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=15
    )
except httpx.HTTPError as error:
    raise SystemExit(
        "Backend connection failed: "
        + type(error).__name__
    )
finally:
    del password

print("Admin Login Status:", response.status_code)

if response.status_code != 200:
    raise SystemExit(
        "STOP: Admin login is not working. "
        "Report preserved. No retest."
    )

print("ADMIN LOGIN: PASS")

pg_password = getpass("PostgreSQL app password: ")

try:
    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="fraudshield_db",
        user="fraudshield_app",
        password=pg_password,
        connect_timeout=10
    ) as connection:

        with connection.cursor() as cursor:
            cursor.execute(
                "SET TRANSACTION READ ONLY"
            )

            cursor.execute("""
                SELECT
                  (SELECT COUNT(*)
                   FROM public.transactions
                   WHERE id = %s),
                  (SELECT COUNT(*)
                   FROM public.predictions
                   WHERE transaction_id = %s),
                  (SELECT COUNT(*)
                   FROM public.alerts
                   WHERE transaction_id = %s)
            """, (internal_id, internal_id, internal_id))

            counts = cursor.fetchone()

except psycopg.Error as error:
    print("PostgreSQL Error:", type(error).__name__)
    raise SystemExit("Database verification failed.")
finally:
    del pg_password

print("Test Transactions:", counts[0])
print("Linked Predictions:", counts[1])
print("Linked Alerts:", counts[2])

if counts != (0, 0, 0):
    raise SystemExit(
        "SAFETY STOP: Existing test records detected. "
        "Report preserved."
    )

print("DATABASE SAFETY CHECK: PASS")

archive = ROOT / "reports" / "phase8" / "archive"
archive.mkdir(parents=True, exist_ok=True)

name = (
    "high_risk_login401_"
    + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    + ".json"
)

destination = archive / name

if destination.exists():
    raise SystemExit("SAFETY STOP: Archive already exists.")

shutil.move(str(REPORT), str(destination))

print("\nPENDING REPORT ARCHIVED!")
print("Admin Login: PASS")
print("Database Test Records: ZERO")
print("Database Records Modified: NONE")
print("HIGH-RISK RETEST: READY")
