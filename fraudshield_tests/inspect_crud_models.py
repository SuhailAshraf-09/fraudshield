from pathlib import Path
import json

import httpx
from app import database, models

print("\nFRAUDSHIELD AI - CRUD MODEL INSPECTION")

Base = getattr(database, "Base", None)

if Base is None:
    Base = getattr(models, "Base", None)

if Base is None:
    raise SystemExit("SQLAlchemy Base missing.")

results = {"tables": {}, "write_apis": []}

for name in (
    "transactions",
    "alerts",
    "predictions",
    "users"
):
    table = Base.metadata.tables.get(name)

    if table is None:
        print("Missing model table:", name)
        continue

    print("\nTABLE:", name)

    columns = []

    for column in table.columns:
        item = {
            "name": column.name,
            "type": str(column.type),
            "nullable": column.nullable,
            "primary_key": column.primary_key,
            "foreign_keys": [
                str(key.column)
                for key in column.foreign_keys
            ]
        }

        columns.append(item)

        print(
            "Field:", column.name,
            "| Type:", column.type,
            "| Required:", (
                not column.nullable
                and not column.primary_key
                and column.default is None
                and column.server_default is None
            ),
            "| Primary Key:", column.primary_key
        )

    results["tables"][name] = columns

print("\nREGISTERED WRITE ENDPOINTS")

try:
    response = httpx.get(
        "http://127.0.0.1:8000/openapi.json",
        timeout=10
    )
    response.raise_for_status()

    paths = response.json().get("paths", {})

    for path, methods in sorted(paths.items()):
        for method in ("post", "put", "patch", "delete"):
            if method not in methods:
                continue

            entry = {
                "method": method.upper(),
                "path": path
            }

            results["write_apis"].append(entry)

            print(
                entry["method"],
                entry["path"]
            )

except httpx.HTTPError as error:
    print("Live API inspection unavailable.")
    print("Error type:", type(error).__name__)

report = Path(
    "reports/phase7/crud_model_inspection.json"
)

report.parent.mkdir(
    parents=True,
    exist_ok=True
)

report.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nCRUD MODEL INSPECTION COMPLETED")
print("Report:", report)
print("No database records modified.")
