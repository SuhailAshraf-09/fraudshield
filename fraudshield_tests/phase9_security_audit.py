import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports" / "phase9"

BASE = "http://127.0.0.1:8000"

print("\nFRAUDSHIELD AI - PHASE 9 SECURITY AUDIT")

protected_get = [
    "/api/v1/auth/me",
    "/api/v1/transactions",
    "/api/v1/alerts",
    "/api/v1/dashboard/summary"
]

protected_post = [
    "/api/v1/ml/predict",
    "/api/v1/ml/batch-predict",
    "/api/v1/ml/report-pdf",
    "/api/v1/ml/predict-and-save",
    "/api/v1/predictions"
]

results = {
    "audit": "phase9_security_baseline",
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "get_tests": {},
    "post_declarations": {},
    "checks_passed": False
}

with httpx.Client(
    base_url=BASE,
    timeout=15,
    follow_redirects=False
) as client:

    response = client.get("/openapi.json")
    response.raise_for_status()

    spec = response.json()
    paths = spec.get("paths", {})

    print("OpenAPI: PASS")

    print("\nSTEP 1 - PROTECTED GET ENDPOINTS")

    for path in protected_get:

        operation = paths.get(path, {}).get("get")

        if operation is None:
            results["get_tests"][path] = {
                "registered": False,
                "passed": False
            }
            print("MISSING:", path)
            continue

        security = operation.get(
            "security",
            spec.get("security", [])
        )

        without_token = client.get(path)

        invalid_token = client.get(
            path,
            headers={
                "Authorization":
                "Bearer invalid.test.token"
            }
        )

        passed = (
            bool(security)
            and without_token.status_code == 401
            and invalid_token.status_code == 401
        )

        results["get_tests"][path] = {
            "registered": True,
            "jwt_declared": bool(security),
            "unauthorized_status":
                without_token.status_code,
            "invalid_token_status":
                invalid_token.status_code,
            "passed": passed
        }

        print("\nEndpoint:", path)
        print("JWT Declared:", bool(security))
        print(
            "No Token:", without_token.status_code
        )
        print(
            "Invalid Token:", invalid_token.status_code
        )
        print("Check Passed:", passed)

    print("\nSTEP 2 - ML WRITE API SECURITY DECLARATIONS")

    for path in protected_post:

        operation = paths.get(path, {}).get("post")

        if operation is None:
            results["post_declarations"][path] = False
            print("MISSING:", path)
            continue

        declared = bool(
            operation.get(
                "security",
                spec.get("security", [])
            )
        )

        results["post_declarations"][path] = declared

        print("Endpoint:", path)
        print("JWT Declared:", declared)

results["checks_passed"] = (
    all(
        item["passed"]
        for item in results["get_tests"].values()
    )
    and all(results["post_declarations"].values())
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)

report = REPORT_DIR / (
    "security_baseline_"
    + datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )
    + ".json"
)

with report.open("x", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2)

print("\nPHASE 9 SECURITY AUDIT RESULTS")
print("checks_passed:", results["checks_passed"])
print("Report:", report)
print("No database write requests submitted.")

if not results["checks_passed"]:
    raise SystemExit(
        "SECURITY REVIEW REQUIRED - CHECK AUDIT DETAILS"
    )

print("\nSECURITY BASELINE TEST PASSED!")
