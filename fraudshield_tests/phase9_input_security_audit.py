import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException
from pydantic import ValidationError

from app.main import app
from app.ml_persistence_router import (
    PredictAndSaveRequest,
    FEATURES,
    validate_features,
)
from app.ml_persistence_router import router as storage_router

print("\nFRAUDSHIELD AI - INPUT SECURITY AUDIT")

features = {name: 0.0 for name in FEATURES}

valid_payload = {
    "transaction_id": "SECURITY-TEST-ONLY",
    "amount_minor": 100,
    "currency": "USD",
    "occurred_at": datetime.now(timezone.utc).isoformat(),
    "features": features,
}

results = {}

def expect_validation_failure(name, payload):
    try:
        PredictAndSaveRequest.model_validate(payload)
        passed = False
    except ValidationError:
        passed = True

    results[name] = passed
    print(name, ":", "PASS" if passed else "REVIEW")


def expect_feature_failure(name, values):
    try:
        validate_features(values)
        passed = False
    except HTTPException as error:
        passed = error.status_code == 422

    results[name] = passed
    print(name, ":", "PASS" if passed else "REVIEW")


print("\nSTEP 1 - PYDANTIC INPUT VALIDATION")

expect_validation_failure(
    "negative_amount",
    {**valid_payload, "amount_minor": -100}
)

expect_validation_failure(
    "invalid_currency_length",
    {**valid_payload, "currency": "US"}
)

expect_validation_failure(
    "blank_transaction_id",
    {**valid_payload, "transaction_id": ""}
)

expect_validation_failure(
    "invalid_feature_type",
    {
        **valid_payload,
        "features": {**features, "V1": "invalid"}
    }
)

print("\nSTEP 2 - ML FEATURE VALIDATION")

expect_feature_failure(
    "missing_feature",
    {k: v for k, v in features.items() if k != "V28"}
)

expect_feature_failure(
    "unexpected_feature",
    {**features, "Unexpected": 1.0}
)

expect_feature_failure(
    "nan_feature",
    {**features, "V1": float("nan")}
)

expect_feature_failure(
    "infinite_feature",
    {**features, "V1": float("inf")}
)

results["valid_feature_schema"] = len(FEATURES) == 30

print(
    "valid_feature_schema:",
    results["valid_feature_schema"]
)

print("\nSTEP 3 - AUTHORIZATION POLICY INSPECTION")

prediction_route = next(
    (
        route for route in app.routes
        if getattr(route, "path", None)
        == "/api/v1/predictions"
        and "POST" in getattr(route, "methods", set())
    ),
    None
)

if prediction_route is None:
    raise SystemExit("Prediction storage endpoint not found.")

def dependency_names(dependant):
    names = set()
    visited = set()

    def walk(item):
        for dep in item.dependencies:
            if id(dep) in visited:
                continue

            visited.add(id(dep))
            names.add(
                getattr(dep.call, "__name__", "")
            )
            walk(dep)

    walk(dependant)
    return sorted(names)


old_dependencies = dependency_names(
    prediction_route.dependant
)

new_route = next(
    route for route in storage_router.routes
    if route.path == "/predict-and-save"
)

new_dependencies = dependency_names(
    new_route.dependant
)

print("\nExisting /api/v1/predictions")
print("Dependencies:", old_dependencies)

print("\nNew /api/v1/ml/predict-and-save")
print("Dependencies:", new_dependencies)

policy_review = (
    "current_user" in old_dependencies
    and "reviewer_or_admin" not in old_dependencies
)

print("\nExisting Prediction Role Policy Review:", policy_review)

passed = all(results.values())

report = Path("reports/phase9/input_security_audit.json")
report.parent.mkdir(parents=True, exist_ok=True)

report.write_text(
    json.dumps({
        "validation_results": results,
        "validation_checks_passed": passed,
        "existing_prediction_dependencies": old_dependencies,
        "ml_storage_dependencies": new_dependencies,
        "existing_prediction_role_policy_review": policy_review,
        "database_modified": False,
        "live_api_write_tested": False
    }, indent=2),
    encoding="utf-8"
)

print("\nFINAL RESULTS")
print("Validation Checks Passed:", passed)
print("Existing Prediction Policy Review:", policy_review)
print("Report:", report)
print("No database records modified.")

if not passed:
    raise SystemExit("INPUT SECURITY REVIEW REQUIRED")

print("\nINPUT VALIDATION AUDIT PASSED!")