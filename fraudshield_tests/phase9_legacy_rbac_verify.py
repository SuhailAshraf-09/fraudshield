import json
from pathlib import Path

from fastapi.testclient import TestClient
from fastapi.routing import APIRoute

from app.main import app
from app.models import User
from app.database import get_db
from app.security import current_user, reviewer_or_admin

print("\nFRAUDSHIELD AI - PHASE 9 STEP 9S")
print("LEGACY PREDICTION RBAC VERIFICATION")

PATH = "/api/v1/predictions"

routes = [
    r for r in app.routes
    if isinstance(r, APIRoute)
    and r.path == PATH
    and "POST" in r.methods
]

if len(routes) != 1:
    raise SystemExit(
        "SAFETY STOP: Legacy prediction route mismatch."
    )

route = routes[0]

guarded = any(
    dep.call is reviewer_or_admin
    for dep in route.dependant.dependencies
)

print("Prediction Route: FOUND")
print("Reviewer/Admin Guard:", guarded)

if not guarded:
    raise SystemExit(
        "SECURITY FIX STILL REQUIRED. "
        "No backend files changed."
    )

if app.dependency_overrides:
    raise SystemExit(
        "SAFETY STOP: Existing dependency overrides."
    )

def block_database():
    return None  # No database connection required for invalid test payload

def make_user_override(user):
    def override():
        return user
    return override

results = {}
client = TestClient(
    app,
    raise_server_exceptions=False
)

try:
    app.dependency_overrides[get_db] = block_database

    for role, expected in (
        ("admin", 422),
        ("reviewer", 422),
        ("viewer", 403)
    ):
        user = User(
            email=f"test-{role}@example.invalid",
            password_hash="synthetic-only",
            role=role
        )

        app.dependency_overrides[current_user] = (
            make_user_override(user)
        )

        response = client.post(
            PATH,
            json={}
        )

        passed = response.status_code == expected

        results[role] = {
            "status": response.status_code,
            "expected": expected,
            "passed": passed
        }

        print(
            role.upper(),
            "HTTP:", response.status_code,
            "PASS:", passed
        )

finally:
    app.dependency_overrides.clear()
    client.close()

all_passed = all(
    item["passed"]
    for item in results.values()
)

report = Path(
    "reports/phase9/legacy_prediction_rbac.json"
)

report.parent.mkdir(
    parents=True,
    exist_ok=True
)

report.write_text(
    json.dumps({
        "guard_present": guarded,
        "http_results": results,
        "checks_passed": all_passed,
        "real_jwt_tested": False,
        "database_writes_performed": False
    }, indent=2),
    encoding="utf-8"
)

print("\nchecks_passed:", all_passed)
print("Database writes: NONE")
print("Report:", report)

if not all_passed:
    raise SystemExit("RBAC SECURITY REVIEW REQUIRED")

print("\nPHASE 9 STEP 9S PASSED!")

