from getpass import getpass
from pathlib import Path
import json

import httpx

print("\nFRAUDSHIELD AI - POSTGRESQL APPLICATION API TEST")

BASE = "http://127.0.0.1:8000"
REPORT = Path("reports/phase7/postgres_app_api_test.json")

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

results = {}

with httpx.Client(timeout=30) as client:

    schema = client.get(BASE + "/openapi.json")
    print("OpenAPI Status:", schema.status_code)
    schema.raise_for_status()

    paths = schema.json()["paths"]

    login = client.post(
        BASE + "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    del password

    print("Admin Login:", login.status_code)
    results["login"] = login.status_code

    if login.status_code != 200:
        raise SystemExit("Admin login failed.")

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Confirm protected account access.
    me_path = "/api/v1/auth/me"

    unauthorized = client.get(BASE + me_path)
    authorized = client.get(
        BASE + me_path,
        headers=headers
    )

    results["unauthorized_profile"] = unauthorized.status_code
    results["authorized_profile"] = authorized.status_code

    print("Unauthorized Profile:", unauthorized.status_code)
    print("Authorized Profile:", authorized.status_code)

    # Read-only application endpoints.
    checks = {
        "transactions": "/api/v1/transactions",
        "alerts": "/api/v1/alerts",
        "dashboard": "/api/v1/dashboard/summary"
    }

    for name, path in checks.items():

        if path not in paths or "get" not in paths[path]:
            print(name, ": GET endpoint not registered")
            results[name] = "NOT_REGISTERED"
            continue

        response = client.get(
            BASE + path,
            headers=headers
        )

        results[name] = response.status_code
        print(name, "status:", response.status_code)

results["checks_passed"] = (
    results["login"] == 200
    and results["unauthorized_profile"] == 401
    and results["authorized_profile"] == 200
    and all(
        results[name] == 200
        for name in ("transactions", "alerts", "dashboard")
    )
)

REPORT.parent.mkdir(parents=True, exist_ok=True)

REPORT.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFINAL RESULTS")
print("checks_passed:", results["checks_passed"])
print("Report saved:", REPORT)

if not results["checks_passed"]:
    raise SystemExit("Application API review required.")

print("POSTGRESQL APPLICATION API TESTS PASSED!")
