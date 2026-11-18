import json
from pathlib import Path
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models import User
from app.database import get_db
from app.security import current_user, reviewer_or_admin

from app.ml_integrated_router import router as ml_router
from app.ml_persistence_router import router as save_router

print("\nFRAUDSHIELD AI - HTTP RBAC TEST V3")
print("PostgreSQL password: NOT REQUIRED")
print("Database connection: NOT REQUIRED")

targets = {
    "/api/v1/ml/predict": (
        ml_router, "/api/v1/ml/predict"
    ),
    "/api/v1/ml/predict-and-save": (
        save_router, "/predict-and-save"
    )
}

# Verify real router security declarations.
spec = app.openapi()

for path, (router, local_path) in targets.items():

    operation = spec["paths"].get(
        path, {}
    ).get("post")

    if not operation or not operation.get("security"):
        raise SystemExit("JWT declaration missing: " + path)

    routes = [
        route for route in router.routes
        if route.path == local_path
        and "POST" in route.methods
    ]

    if len(routes) != 1:
        raise SystemExit("Router not found: " + path)

    guarded = any(
        dep.call is reviewer_or_admin
        for dep in routes[0].dependant.dependencies
    )

    if not guarded:
        raise SystemExit("RBAC guard missing: " + path)

    print("Protected Router:", path, "PASS")


# Prevent database usage during synthetic requests.
class BlockedDatabase:
    def __getattr__(self, name):
        raise RuntimeError(
            "Database operations prohibited during RBAC test"
        )


def disable_database():
    return BlockedDatabase()


if app.dependency_overrides:
    raise SystemExit(
        "SAFETY STOP: Existing dependency overrides."
    )

results = {}

try:
    app.dependency_overrides[get_db] = disable_database

    with TestClient(
        app,
        raise_server_exceptions=False
    ) as client:

        for role in ("admin", "reviewer", "viewer"):

            fake_user = User(
                email=f"test-{role}@example.invalid",
                password_hash="synthetic-test-only",
                role=role
            )

            def fake_authentication(user=fake_user):
                return user

            # No arguments must be exposed to FastAPI.
            def override_user():
                return fake_user

            app.dependency_overrides[current_user] = (
                override_user
            )

            results[role] = {}

            print("\nTEST ROLE:", role.upper())

            for path in targets:

                # Deliberately invalid payload.
                # No ML prediction or database write.
                response = client.post(
                    path,
                    json={}
                )

                expected = (
                    403 if role == "viewer" else 422
                )

                passed = response.status_code == expected

                results[role][path] = {
                    "actual_status": response.status_code,
                    "expected_status": expected,
                    "passed": passed
                }

                print("Endpoint:", path)
                print("HTTP Status:", response.status_code)
                print("Expected:", expected)
                print("PASS:", passed)

finally:
    app.dependency_overrides.clear()


all_passed = all(
    item["passed"]
    for role_results in results.values()
    for item in role_results.values()
)

output = Path("reports/phase9/http_rbac_v3.json")
output.parent.mkdir(parents=True, exist_ok=True)

output.write_text(
    json.dumps({
        "test_type": "in_process_http_rbac",
        "synthetic_users": True,
        "real_jwt_tested": False,
        "database_access_blocked": True,
        "results": results,
        "checks_passed": all_passed,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat()
    }, indent=2),
    encoding="utf-8"
)

print("\nFINAL RESULTS")
print("checks_passed:", all_passed)
print("Report:", output)
print("No database write requests submitted.")

if not all_passed:
    raise SystemExit("RBAC HTTP TEST NEEDS REVIEW")

print("\nHTTP RBAC V3 TEST PASSED!")