import asyncio
import inspect
import json
from pathlib import Path

from fastapi import HTTPException

from app.models import User
from app.security import reviewer_or_admin
from app.ml_integrated_router import router as ml_router
from app.ml_persistence_router import router as save_router

print("\nFRAUDSHIELD AI - ROLE ENFORCEMENT TEST")

results = {}

# STEP 1: Verify authorization guard attachment.
print("\nSTEP 1 - ROUTER GUARD VERIFICATION")

for name, router in (
    ("ml_prediction", ml_router),
    ("ml_prediction_storage", save_router)
):
    dependencies = []

    for route in router.routes:
        for dep in route.dependant.dependencies:
            function = dep.call
            dependencies.append(
                getattr(function, "__name__", "")
            )

    guarded = "reviewer_or_admin" in dependencies

    results[name] = guarded

    print(name, "guard:", guarded)


# STEP 2: Test actual role authorization function.
print("\nSTEP 2 - ROLE ENFORCEMENT")

parameters = list(
    inspect.signature(
        reviewer_or_admin
    ).parameters.values()
)

if len(parameters) != 1:
    raise SystemExit(
        "REVIEW REQUIRED: Unexpected guard signature."
    )

parameter_name = parameters[0].name

def test_role(role):
    # In-memory ORM user: nothing saved to PostgreSQL.
    user = User(
        email="rbac-test@example.invalid",
        password_hash="synthetic-test-only",
        role=role
    )

    try:
        outcome = reviewer_or_admin(
            **{parameter_name: user}
        )

        if inspect.isawaitable(outcome):
            asyncio.run(outcome)

        return {
            "allowed": True,
            "http_status": None
        }

    except HTTPException as error:
        return {
            "allowed": False,
            "http_status": error.status_code
        }

    except Exception as error:
        return {
            "allowed": False,
            "http_status": None,
            "error_type": type(error).__name__
        }


for role in ("admin", "reviewer", "viewer"):
    outcome = test_role(role)

    results[role] = outcome

    print("\nRole:", role)
    print("Allowed:", outcome["allowed"])
    print("HTTP Status:", outcome["http_status"])

    if "error_type" in outcome:
        print("Error Type:", outcome["error_type"])


results["checks_passed"] = (
    results["ml_prediction"]
    and results["ml_prediction_storage"]
    and results["admin"]["allowed"] is True
    and results["reviewer"]["allowed"] is True
    and results["viewer"]["allowed"] is False
    and results["viewer"]["http_status"] == 403
)

report = Path(
    "reports/phase9/role_enforcement_test.json"
)

report.parent.mkdir(
    parents=True,
    exist_ok=True
)

report.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nFINAL ROLE SECURITY RESULTS")
print("checks_passed:", results["checks_passed"])
print("Report:", report)
print("Database records modified: NONE")
print("Live API requests submitted: NONE")

if not results["checks_passed"]:
    raise SystemExit(
        "ROLE ENFORCEMENT REVIEW REQUIRED"
    )

print("\nROLE ENFORCEMENT UNIT TEST PASSED!")
