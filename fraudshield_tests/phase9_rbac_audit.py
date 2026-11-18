import json
from pathlib import Path
from datetime import datetime, timezone

from fastapi.routing import APIRoute
from app.main import app

print("\nFRAUDSHIELD AI - PHASE 9 RBAC AUDIT")

endpoints = [
    "/api/v1/ml/predict",
    "/api/v1/ml/batch-predict",
    "/api/v1/ml/report-pdf",
    "/api/v1/ml/predict-and-save",
    "/api/v1/predictions"
]

schema = app.openapi()
results = {}

def collect_dependencies(dependant, visited=None):
    if visited is None:
        visited = set()

    names = []

    for item in dependant.dependencies:
        if id(item) in visited:
            continue

        visited.add(id(item))

        function = item.call
        name = getattr(
            function,
            "__name__",
            type(function).__name__
        )

        names.append(name)
        names.extend(
            collect_dependencies(item, visited)
        )

    return sorted(set(names))


for path in endpoints:
    print("\nENDPOINT:", path)

    route = next(
        (
            item for item in app.routes
            if isinstance(item, APIRoute)
            and item.path == path
            and "POST" in item.methods
        ),
        None
    )

    if route is None:
        print("Status: MISSING")
        results[path] = {
            "registered": False,
            "jwt_declared": False,
            "reviewer_admin_guard": False
        }
        continue

    operation = schema["paths"][path]["post"]

    jwt_declared = bool(
        operation.get(
            "security",
            schema.get("security", [])
        )
    )

    dependencies = collect_dependencies(
        route.dependant
    )

    role_guard = (
        "reviewer_or_admin" in dependencies
    )

    results[path] = {
        "registered": True,
        "jwt_declared": jwt_declared,
        "reviewer_admin_guard": role_guard,
        "dependencies": dependencies
    }

    print("JWT Declared:", jwt_declared)
    print("Reviewer/Admin Guard:", role_guard)
    print("Security Dependencies:", dependencies)

    if not jwt_declared:
        print("REVIEW: JWT declaration missing")
    elif not role_guard:
        print("REVIEW: Explicit role guard not detected")
    else:
        print("Role Guard Declaration: FOUND")


all_registered = all(
    item["registered"]
    for item in results.values()
)

all_jwt = all(
    item["jwt_declared"]
    for item in results.values()
)

role_guard_count = sum(
    item["reviewer_admin_guard"]
    for item in results.values()
)

report = {
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "all_routes_registered": all_registered,
    "all_jwt_declared": all_jwt,
    "role_guards_detected": role_guard_count,
    "total_routes": len(endpoints),
    "results": results,
    "note": (
        "Static dependency inspection only. "
        "Runtime role enforcement requires separate tests."
    )
}

output = Path(
    "reports/phase9/rbac_dependency_audit.json"
)

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

output.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("\nPHASE 9 RBAC AUDIT RESULTS")
print("All Routes Registered:", all_registered)
print("All JWT Declared:", all_jwt)
print(
    "Reviewer/Admin Guards:",
    role_guard_count,
    "of",
    len(endpoints)
)

print("Report:", output)
print("No database records modified.")
print("No API write requests submitted.")
print("\nRBAC DEPENDENCY AUDIT COMPLETED")
