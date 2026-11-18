import ast
import inspect
import json
import textwrap
from pathlib import Path

from app.main import app
from app import models, database

print("\nFRAUDSHIELD AI - PHASE 8 ML STORAGE AUDIT")

report = {
    "endpoints": {},
    "tables": {},
    "model_artifact": None
}

# Inspect registered prediction endpoints.
for path in (
    "/api/v1/ml/predict",
    "/api/v1/predictions",
    "/api/v1/ml/batch-predict"
):
    routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == path
        and "POST" in getattr(route, "methods", set())
    ]

    print("\nENDPOINT:", path)
    print("Registered:", bool(routes))

    if not routes:
        continue

    endpoint = routes[0].endpoint
    source = textwrap.dedent(
        inspect.getsource(endpoint)
    )

    tree = ast.parse(source)

    function_calls = sorted({
        ast.unparse(node.func)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    })

    relevant_calls = [
        call for call in function_calls
        if any(word in call.lower() for word in (
            "predict",
            "model",
            "load",
            "score",
            "risk",
            "db.add",
            "db.commit",
            "session",
            "tier"
        ))
    ]

    print("Handler:", endpoint.__name__)
    print("Module:", endpoint.__module__)

    print("Relevant Calls:")
    for call in relevant_calls:
        print(" -", call)

    report["endpoints"][path] = {
        "handler": endpoint.__name__,
        "module": endpoint.__module__,
        "relevant_calls": relevant_calls
    }

# Inspect existing SQLAlchemy model tables.
Base = getattr(database, "Base", None)

if Base is None:
    Base = getattr(models, "Base", None)

if Base is None:
    raise SystemExit("SQLAlchemy Base not found.")

print("\nDATABASE MODEL STRUCTURE")

for name in ("transactions", "predictions", "alerts"):
    table = Base.metadata.tables.get(name)

    if table is None:
        print("Missing table:", name)
        continue

    print("\nTABLE:", name)

    fields = []

    for column in table.columns:
        details = {
            "name": column.name,
            "type": str(column.type),
            "nullable": column.nullable,
            "primary_key": column.primary_key,
            "foreign_keys": [
                str(fk.target_fullname)
                for fk in column.foreign_keys
            ]
        }

        fields.append(details)

        print(
            column.name,
            "|", column.type,
            "| PK:", column.primary_key,
            "| FK:", details["foreign_keys"]
        )

    report["tables"][name] = fields

# Verify the trained model artifact exists.
model_path = Path("ml_models/random_forest_v1.joblib")

report["model_artifact"] = {
    "path": str(model_path),
    "exists": model_path.is_file()
}

print("\nTRAINED RANDOM FOREST MODEL")
print("Model Exists:", model_path.is_file())

output = Path("reports/phase8/ml_storage_audit.json")
output.parent.mkdir(parents=True, exist_ok=True)

output.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("\nPHASE 8 AUDIT COMPLETED")
print("Report:", output)
print("No database records modified.")
print("No API requests submitted.")
