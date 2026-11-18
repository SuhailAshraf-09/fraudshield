from pathlib import Path
from datetime import datetime
import subprocess
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "app" / "main.py"

MARKER = "# FRAUDSHIELD ML PERSISTENCE ROUTER V1"
NEW_ROUTE = "/api/v1/ml/predict-and-save"

print("\nFRAUDSHIELD AI - ML PERSISTENCE REGISTRATION")

if not MAIN.is_file():
    raise SystemExit("SAFETY STOP: main.py missing.")

from app.main import app

current_paths = app.openapi().get("paths", {})

if NEW_ROUTE in current_paths:
    print("ML Persistence API already registered.")
    print("No changes made.")
    raise SystemExit(0)

source = MAIN.read_text(encoding="utf-8-sig")

if MARKER in source:
    raise SystemExit(
        "SAFETY STOP: Registration marker already exists."
    )

from app.ml_persistence_router import router

if not any(
    route.path == "/predict-and-save"
    for route in router.routes
):
    raise SystemExit(
        "SAFETY STOP: Persistence route missing."
    )

backup = MAIN.with_name(
    "main.py.backup_phase8_" +
    datetime.now().strftime("%Y%m%d_%H%M%S")
)

shutil.copy2(MAIN, backup)

print("Main backend backup:", backup.name)

snippet = """

# FRAUDSHIELD ML PERSISTENCE ROUTER V1
from app.ml_persistence_router import router as ml_persistence_router

app.include_router(
    ml_persistence_router,
    prefix="/api/v1/ml"
)
"""

try:
    updated = source.rstrip() + "\n" + snippet

    compile(updated, str(MAIN), "exec")

    MAIN.write_text(
        updated,
        encoding="utf-8"
    )

    verification = """
from app.main import app

schema = app.openapi()
paths = schema["paths"]

required = [
    "/api/v1/ml/predict",
    "/api/v1/ml/batch-predict",
    "/api/v1/ml/report-pdf",
    "/api/v1/ml/predict-and-save"
]

for path in required:
    assert path in paths, f"Missing endpoint: {path}"
    print("API VERIFIED:", path)

operation = paths[
    "/api/v1/ml/predict-and-save"
]["post"]

assert operation.get("security"), (
    "JWT security not declared."
)

print("JWT SECURITY: VERIFIED")
print("ALL ML ROUTES REGISTERED SUCCESSFULLY!")
"""

    result = subprocess.run(
        [sys.executable, "-c", verification],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=45
    )

    if result.returncode != 0:
        print(result.stderr[-1500:])
        raise RuntimeError(
            "API registration verification failed."
        )

    print(result.stdout)
    print("Existing API routes: PRESERVED")
    print("PostgreSQL records: UNCHANGED")

except Exception as error:
    shutil.copy2(backup, MAIN)
    print("Original main.py restored.")
    print("Error:", type(error).__name__)
    raise SystemExit(1)
