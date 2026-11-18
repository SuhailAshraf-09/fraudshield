import os
import json
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parent.parent

print("\nFRAUDSHIELD AI - HTTP RBAC INTEGRATION TEST")

password = getpass("PostgreSQL app password: ")

url = URL.create(
    "postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

os.environ["FRAUDSHIELD_DATABASE_URL"] = (
    url.render_as_string(hide_password=False)
)

del password
del url

# Import after PostgreSQL configuration.
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import app
from app.database import engine
from app.models import User
from app.security import current_user, reviewer_or_admin

if engine.dialect.name != "postgresql":
    raise SystemExit("SAFETY STOP: Incorrect database engine.")

TARGETS = [
    "/api/v1/ml/predict",
    "/api/v1/ml/predict-and-save"
]

def has_role_guard(node):
    for dep in node.dependencies:
        if dep.call is reviewer_or_admin:
            return True
        if has_role_guard(dep):
            return True
    return False

print("\nSTEP 1 - FASTAPI ROUTE VALIDATION")

for path in TARGETS:
    routes = [
        r for r in app.routes
        if isinstance(r, APIRoute)
        and r.path == path
        and "POST" in r.methods
    ]

    if len(routes) != 1:
        raise SystemExit(
            "SAFETY STOP: Expected one route: " + path
        )

    if not has_role_guard(routes[0].dependant):
        raise SystemExit(
            "SAFETY STOP: Role guard missing: " + path
        )

    print("Role Guard Verified:", path)

def database_counts():
    with engine.connect() as conn:
        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong database identity.")

        counts = {}

        for name in (
            "users", "transactions",
            "predictions", "alerts"
        ):
            counts[name] = conn.execute(
                text(f"SELECT COUNT(*) FROM public.{name}")
            ).scalar_one()

        return counts

before = database_counts()
print("\nDatabase Counts Before:", before)

if current_user in app.dependency_overrides:
    raise SystemExit(
        "SAFETY STOP: Authentication already overridden."
    )

results = {}
client = TestClient(
    app,
    raise_server_exceptions=False
)

try:
    for role in ("admin", "reviewer", "viewer"):

        # Synthetic in-memory user; no database write.
        fake_user = User(
            email=f"rbac-{role}@example.invalid",
            password_hash="synthetic-test-only",
            role=role
        )

        def override_user(user=fake_user):
            return user

        # Zero-argument wrapper for FastAPI dependency injection.
        def user_dependency():
            return fake_user

        app.dependency_overrides[current_user] = (
            user_dependency
        )

        results[role] = {}

        print("\nROLE:", role.upper())

        for path in TARGETS:
            # Empty body guarantees no valid prediction
            # or database write operation is submitted.
            response = client.post(
                path,
                json={}
            )

            expected = (
                403 if role == "viewer" else 422
            )

            passed = response.status_code == expected

            results[role][path] = {
                "http_status": response.status_code,
                "expected_status": expected,
                "passed": passed
            }

            print("Endpoint:", path)
            print("HTTP Status:", response.status_code)
            print("Expected:", expected)
            print("Check:", "PASS" if passed else "FAIL")

finally:
    app.dependency_overrides.pop(current_user, None)
    client.close()

after = database_counts()

print("\nDatabase Counts After:", after)

counts_unchanged = before == after

passed = (
    counts_unchanged
    and all(
        check["passed"]
        for role_tests in results.values()
        for check in role_tests.values()
    )
)

report_dir = ROOT / "reports" / "phase9"
report_dir.mkdir(parents=True, exist_ok=True)

report_path = report_dir / (
    "http_rbac_"
    + datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )
    + ".json"
)

report = {
    "test_type": "in_process_fastapi_http_rbac",
    "real_jwt_tested": False,
    "note": "Synthetic users via local dependency override",
    "role_results": results,
    "counts_before": before,
    "counts_after": after,
    "counts_unchanged": counts_unchanged,
    "checks_passed": passed
}

with report_path.open("x", encoding="utf-8") as file:
    json.dump(report, file, indent=2)

print("\nFINAL SECURITY RESULTS")
print("Database Counts Unchanged:", counts_unchanged)
print("checks_passed:", passed)
print("Report:", report_path)

if not passed:
    raise SystemExit("RBAC HTTP TEST REVIEW REQUIRED")

print("\nFASTAPI HTTP ROLE TEST PASSED!")
