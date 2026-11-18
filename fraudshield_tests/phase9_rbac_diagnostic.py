import json
from pathlib import Path

import httpx
from fastapi.routing import APIRoute

from app.main import app

print("\nFRAUDSHIELD AI - RBAC DIAGNOSTIC")

TARGETS = [
    "/api/v1/ml/predict",
    "/api/v1/ml/batch-predict",
    "/api/v1/ml/report-pdf",
    "/api/v1/ml/predict-and-save",
    "/api/v1/predictions",
]

def dependencies_of(dependant):
    names = set()
    visited = set()

    def walk(node):
        for dependency in node.dependencies:
            if id(dependency) in visited:
                continue

            visited.add(id(dependency))
            function = dependency.call

            name = getattr(
                function,
                "__name__",
                type(function).__name__
            )

            names.add(name)
            walk(dependency)

    walk(dependant)
    return sorted(names)


print("\nSTEP 1 - LOCAL FASTAPI ROUTES")

local_routes = {}

for route in app.routes:
    if not isinstance(route, APIRoute):
        continue

    if "POST" not in route.methods:
        continue

    local_routes[route.path] = route

for path in TARGETS:
    route = local_routes.get(path)

    print("\nEndpoint:", path)
    print("Local Registered:", route is not None)

    if route is not None:
        names = dependencies_of(route.dependant)

        print("Dependencies:", names)
        print(
            "Reviewer/Admin Guard:",
            "reviewer_or_admin" in names
        )
        print(
            "Current User Guard:",
            "current_user" in names
        )


print("\nSTEP 2 - LIVE SERVER COMPARISON")

live_results = {}

try:
    response = httpx.get(
        "http://127.0.0.1:8000/openapi.json",
        timeout=15
    )

    response.raise_for_status()
    paths = response.json().get("paths", {})

    print("Live OpenAPI Status:", response.status_code)

    for path in TARGETS:
        operation = paths.get(path, {}).get("post")

        registered = operation is not None

        jwt_declared = (
            bool(operation.get("security"))
            if registered else False
        )

        local = local_routes.get(path)

        live_results[path] = {
            "local_registered": local is not None,
            "live_registered": registered,
            "jwt_declared": jwt_declared,
            "local_dependencies": (
                dependencies_of(local.dependant)
                if local is not None else []
            )
        }

        print("\nEndpoint:", path)
        print("LIVE Registered:", registered)
        print("LIVE JWT Declared:", jwt_declared)

except httpx.HTTPError as error:
    print(
        "LIVE SERVER CHECK FAILED:",
        type(error).__name__
    )


print("\nSTEP 3 - ALL LOCAL ML ROUTES")

for path in sorted(local_routes):
    if "/ml/" in path or "/predictions" in path:
        print(path)


output = Path(
    "reports/phase9/rbac_diagnostic.json"
)

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

output.write_text(
    json.dumps(live_results, indent=2),
    encoding="utf-8"
)

print("\nRBAC DIAGNOSTIC COMPLETED")
print("Report:", output)
print("Database records: UNCHANGED")
print("No write API requests submitted.")
