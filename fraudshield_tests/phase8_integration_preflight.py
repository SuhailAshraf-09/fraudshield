import inspect
import re

from app.main import app
from app.models import Base
from app.ml_integrated_router import FEATURES, load_model

print("\nFRAUDSHIELD AI - PHASE 8 INTEGRATION PREFLIGHT")

print("\nSTEP 1 - DATABASE FIELD MAPPING")

for name in ("transactions", "predictions", "alerts"):
    table = Base.metadata.tables[name]

    print("\nTABLE:", name)

    for column in table.columns:
        required = (
            not column.nullable
            and not column.primary_key
            and column.default is None
            and column.server_default is None
        )

        print(
            column.name,
            "|", column.type,
            "| Required:", required,
            "| PK:", column.primary_key
        )

print("\nSTEP 2 - EXISTING PREDICTION LOGIC")

route = next(
    (
        r for r in app.routes
        if getattr(r, "path", None)
        == "/api/v1/predictions"
        and "POST" in getattr(r, "methods", set())
    ),
    None
)

if route is None:
    raise SystemExit("Prediction endpoint missing.")

source = inspect.getsource(route.endpoint).splitlines()

keywords = re.compile(
    r"Transaction\(|Prediction\(|Alert\(|"
    r"risk|score|tier|features|"
    r"db\.add|db\.flush|db\.commit",
    re.IGNORECASE
)

indices = set()

for index, line in enumerate(source):
    if keywords.search(line):
        indices.update(
            range(max(0, index - 1),
                  min(len(source), index + 3))
        )

for index in sorted(indices):
    print(f"{index + 1:03d}: {source[index]}")

print("\nSTEP 3 - TRAINED RANDOM FOREST")

print("Expected ML Features:", len(FEATURES))
print("Feature Names:", FEATURES)

model, threshold = load_model()

print("Model Loaded:", model is not None)
print("Classification Threshold:", threshold)

print("\nINTEGRATION PREFLIGHT COMPLETED")
print("No database records modified.")
print("No API requests submitted.")
