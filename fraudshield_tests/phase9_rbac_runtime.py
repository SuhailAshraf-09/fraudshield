import os
import json
from getpass import getpass
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

print("\nFRAUDSHIELD AI - POSTGRESQL RBAC RUNTIME AUDIT")

password = getpass("PostgreSQL app password: ")

url = URL.create(
    "postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

# Must be configured BEFORE importing app.database
# or app.main.
os.environ["FRAUDSHIELD_DATABASE_URL"] = (
    url.render_as_string(hide_password=False)
)

del password

test_engine = create_engine(
    url,
    hide_parameters=True,
    connect_args={"connect_timeout": 10}
)

try:
    with test_engine.connect() as conn:
        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

    if tuple(identity) != (
        "fraudshield_db", "fraudshield_app"
    ):
        raise RuntimeError("Incorrect PostgreSQL identity")

    print("PostgreSQL Connection: PASS")
    print("Database:", identity[0])
    print("User:", identity[1])

finally:
    test_engine.dispose()

del url

# Import FastAPI only after setting the database URL.
from app.main import app
from app.database import engine as app_engine
from fastapi.routing import APIRoute

if app_engine.dialect.name != "postgresql":
    raise SystemExit("SAFETY STOP: Backend is not PostgreSQL.")

print("Backend Database Engine: PostgreSQL")

targets = [
    "/api/v1/ml/predict",
    "/api/v1/ml/batch-predict",
    "/api/v1/ml/report-pdf",
    "/api/v1/ml/predict-and-save",
    "/api/v1/predictions"
]

def get_dependencies(dependant):
    names = set()
    visited = set()

    def visit(node):
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
            visit(dependency)

    visit(dependant)
    return sorted(names)


spec = app.openapi()
paths = spec.get("paths", {})

results = {}

print("\nSTEP 1 - REGISTERED ML ROUTES")

for path in targets:

    route = next(
        (
            r for r in app.routes
            if isinstance(r, APIRoute)
            and r.path == path
            and "POST" in r.methods
        ),
        None
    )

    operation = paths.get(path, {}).get("post")

    registered = route is not None
    jwt_declared = bool(
        operation.get("security", spec.get("security", []))
    ) if operation else False

    dependencies = (
        get_dependencies(route.dependant)
        if route else []
    )

    role_guard = "reviewer_or_admin" in dependencies
    current_user_guard = "current_user" in dependencies

    results[path] = {
        "registered": registered,
        "jwt_declared": jwt_declared,
        "reviewer_admin_guard": role_guard,
        "current_user_guard": current_user_guard,
        "dependencies": dependencies
    }

    print("\nEndpoint:", path)
    print("Registered:", registered)
    print("JWT Declared:", jwt_declared)
    print("Reviewer/Admin Guard:", role_guard)
    print("Current User Guard:", current_user_guard)
    print("Dependencies:", dependencies)


registered_count = sum(
    item["registered"]
    for item in results.values()
)

jwt_count = sum(
    item["jwt_declared"]
    for item in results.values()
)

role_count = sum(
    item["reviewer_admin_guard"]
    for item in results.values()
)

output = Path(
    "reports/phase9/rbac_postgres_runtime.json"
)

output.parent.mkdir(parents=True, exist_ok=True)

output.write_text(
    json.dumps({
        "database_engine": "postgresql",
        "registered_count": registered_count,
        "jwt_count": jwt_count,
        "reviewer_admin_guard_count": role_count,
        "routes": results,
        "note": "Static runtime-context dependency inspection"
    }, indent=2),
    encoding="utf-8"
)

print("\nPHASE 9 RUNTIME AUDIT RESULTS")
print("Registered Routes:", registered_count, "of 5")
print("JWT Protected Declarations:", jwt_count, "of 5")
print("Reviewer/Admin Guards:", role_count, "of 5")

print("Report:", output)
print("No database records modified.")
print("No API write requests submitted.")
print("\nPOSTGRESQL RBAC RUNTIME AUDIT COMPLETED")
