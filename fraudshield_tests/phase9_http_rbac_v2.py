import os
import json
from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass

from sqlalchemy.engine import URL
from sqlalchemy import text

print("\nFRAUDSHIELD AI - HTTP RBAC TEST V2")

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

# Import after configuring PostgreSQL.
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, get_db
from app.models import User
from app.security import current_user, reviewer_or_admin

from app.ml_integrated_router import router as ml_router
from app.ml_persistence_router import router as storage_router

TARGETS = {
    "/api/v1/ml/predict": (
        ml_router, "/api/v1/ml/predict"
    ),
    "/api/v1/ml/predict-and-save": (
        storage_router, "/predict-and-save"
    )
}

def counts():
    with engine.connect() as conn:
        conn.exec_driver_sql("SET TRANSACTION READ ONLY")

        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong database target.")

        return {
            name: conn.execute(
                text(f"SELECT COUNT(*) FROM public.{name}")
            ).scalar_one()
            for name in (
                "users", "transactions",
                "predictions", "alerts"
            )
        }


print("\nSTEP 1 - VERIFY ROUTERS")

spec = app.openapi()

for path, (router, local_path) in TARGETS.items():

    operation = spec.get("paths", {}).get(
        path, {}
    ).get("post")

    if not operation or not operation.get("security"):
        raise SystemExit(
            "SAFETY STOP: Missing secured API: " + path
        )

    matches = [
        r for r in router.routes
        if r.path == local_path
        and "POST" in r.methods
    ]

    if len(matches) != 1:
        raise SystemExit(
            "SAFETY STOP: Router endpoint mismatch."
        )

    guarded = any(
        dependency.call is reviewer_or_admin
        for dependency in matches[0].dependant.dependencies
    )

    if not guarded:
        raise SystemExit(
            "SAFETY STOP: Role guard missing."
        )

    print("SECURED ROUTE VERIFIED:", path)


print("\nSTEP 2 - HTTP ROLE TESTS")

before = counts()
print("Database Before:", before)

if app.dependency_overrides:
    raise SystemExit(
        "SAFETY STOP: Dependency overrides already exist."
    )

# Prevent database access inside synthetic HTTP tests.
class DisabledDatabase:
    def __getattr__(self, name):
        raise RuntimeError(
            "Database use disabled during RBAC testing."
        )

def override_database():
    return DisabledDatabase()


results = {}
client = TestClient(
    app,
    raise_server_exceptions=False
)

try:
    app.dependency_overrides[get_db] = override_database

    for role in ("admin", "reviewer", "viewer"):

        fake_user = User(
            email=f"rbac-{role}@example.invalid",
            password_hash="synthetic-test-only",
            role=role
        )

        def override_current_user():
            return fake_user

        app.dependency_overrides[current_user] = (
            override_current_user
        )

        results[role] = {}

        print("\nROLE:", role.upper())

        for path in TARGETS:

            # Invalid body: no legitimate ML request
            # or prediction write can be performed.
            response = client.post(
                path,
                json={}
            )

            expected = (
                403 if role == "viewer" else 422
            )

            passed = response.status_code == expected

            results[role][path] = {
                "actual": response.status_code,
                "expected": expected,
                "passed": passed
            }

            print("Endpoint:", path)
            print("HTTP Status:", response.status_code)
            print("Expected:", expected)
            print("PASS:", passed)

finally:
    app.dependency_overrides.clear()
    client.close()


print("\nSTEP 3 - DATABASE INTEGRITY")

after = counts()
unchanged = before == after

print("Database After:", after)
print("Database Unchanged:", unchanged)

all_passed = (
    unchanged
    and all(
        check["passed"]
        for role_results in results.values()
        for check in role_results.values()
    )
)

output_dir = Path("reports/phase9")
output_dir.mkdir(parents=True, exist_ok=True)

output = output_dir / (
    "http_rbac_v2_"
    + datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )
    + ".json"
)

output.write_text(
    json.dumps({
        "test": "in-process HTTP role enforcement",
        "real_jwt_tested": False,
        "dependency_overrides_used": True,
        "results": results,
        "database_before": before,
        "database_after": after,
        "database_unchanged": unchanged,
        "checks_passed": all_passed
    }, indent=2),
    encoding="utf-8"
)

print("\nFINAL RESULTS")
print("checks_passed:", all_passed)
print("Report:", output)

if not all_passed:
    raise SystemExit("HTTP RBAC TEST NEEDS REVIEW")

print("\nHTTP RBAC V2 TEST PASSED!")
