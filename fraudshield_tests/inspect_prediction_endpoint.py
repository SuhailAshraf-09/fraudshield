import json
import httpx

print("\nFRAUDSHIELD AI - PREDICTION WRITE API INSPECTION")

base = "http://127.0.0.1:8000"

response = httpx.get(
    base + "/openapi.json",
    timeout=15
)

response.raise_for_status()

spec = response.json()
paths = spec.get("paths", {})
schemas = spec.get("components", {}).get("schemas", {})

path = "/api/v1/predictions"
operation = paths.get(path, {}).get("post")

if operation is None:
    raise SystemExit("Prediction POST endpoint not found.")

print("\nEndpoint:", "POST", path)
print("Authentication Declared:", bool(
    operation.get("security", spec.get("security", []))
))

print("Summary:", operation.get("summary", "Not specified"))

request_body = operation.get("requestBody", {})
content = request_body.get("content", {})

for media_type, media in content.items():
    print("\nRequest Content Type:", media_type)

    schema = media.get("schema", {})
    print("Request Schema:", json.dumps(schema))

    ref = schema.get("$ref")

    if ref:
        schema_name = ref.split("/")[-1]
        details = schemas.get(schema_name, {})

        print("Schema Name:", schema_name)
        print("Required Fields:", details.get("required", []))

        for name, field in details.get(
            "properties", {}
        ).items():
            print(
                "Field:", name,
                "| Type:", field.get("type", "Referenced"),
                "| Required:",
                name in details.get("required", [])
            )

print("\nDeclared Response Codes:")

for status, detail in operation.get(
    "responses", {}
).items():
    print(status, "-", detail.get("description", ""))

print("\nPREDICTION API INSPECTION COMPLETED")
print("No predictions submitted.")
print("No database records modified.")
