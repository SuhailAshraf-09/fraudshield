from pathlib import Path
import json
import httpx

print("\nFRAUDSHIELD AI - CRUD API INSPECTION")

BASE = "http://127.0.0.1:8000"
REPORT = Path("reports/phase7/crud_api_inspection.json")

with httpx.Client(timeout=15) as client:
    response = client.get(BASE + "/openapi.json")
    response.raise_for_status()
    spec = response.json()

paths = spec.get("paths", {})
schemas = spec.get("components", {}).get("schemas", {})

methods = {"get", "post", "put", "patch", "delete"}
relevant = (
    "/auth/",
    "/transactions",
    "/alerts",
    "/predictions",
    "/dashboard"
)

def describe_schema(schema):
    if not isinstance(schema, dict):
        return [], []

    if "$ref" in schema:
        key = schema["$ref"].split("/")[-1]
        schema = schemas.get(key, {})

    properties = dict(schema.get("properties", {}))
    required = set(schema.get("required", []))

    for part in schema.get("allOf", []):
        fields, needed = describe_schema(part)
        for field in fields:
            properties.setdefault(field, {})
        required.update(needed)

    return sorted(properties), sorted(required)

results = []

for path in sorted(paths):
    if not any(item in path for item in relevant):
        continue

    for method, operation in paths[path].items():
        if method not in methods:
            continue

        security = operation.get(
            "security",
            spec.get("security", [])
        )

        body = operation.get("requestBody", {})
        content = body.get("content", {})

        fields = []
        required = []

        for media in content.values():
            fields, required = describe_schema(
                media.get("schema", {})
            )
            if fields or required:
                break

        item = {
            "method": method.upper(),
            "path": path,
            "authentication_declared": bool(security),
            "request_fields": fields,
            "required_fields": required
        }

        results.append(item)

        print("\n", item["method"], item["path"])
        print("Auth Declared:", bool(security))

        if method in {"post", "put", "patch", "delete"}:
            print("Request Fields:", fields)
            print("Required Fields:", required)

REPORT.parent.mkdir(parents=True, exist_ok=True)

REPORT.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print("\nCRUD API INSPECTION COMPLETED")
print("Report:", REPORT)
print("No API data modified.")
print("No database records modified.")
