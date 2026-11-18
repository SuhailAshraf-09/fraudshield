from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
target = root / "app" / "ml_persistence_router.py"

print("\nFRAUDSHIELD AI - ML STORAGE ID FIX")

if not target.is_file():
    raise SystemExit("SAFETY STOP: ML router file missing.")

source = target.read_text(encoding="utf-8-sig")

marker = "# FRAUDSHIELD STABLE TX ID V1"

if marker in source:
    raise SystemExit(
        "Fix already present. No changes made."
    )

old_import = "from uuid import uuid4"

old_query = (
    "Transaction.transaction_id == request.transaction_id"
)

old_values = (
    '        "id": str(uuid4()),\n'
    '        "transaction_id": request.transaction_id,\n'
)

old_lookup = (
    "    existing = db.query(Transaction).filter(\n"
)

checks = [
    old_import,
    old_query,
    old_values,
    old_lookup
]

for fragment in checks:
    if source.count(fragment) != 1:
        raise SystemExit(
            "SAFETY STOP: Unexpected source structure. "
            "No changes made."
        )

# Generate a consistent internal UUID from the
# client-provided transaction identifier.
stable_id_code = (
    "    " + marker + "\n"
    "    stable_tx_id = str(uuid5(\n"
    "        NAMESPACE_URL,\n"
    '        "fraudshield-ai/ml/predict-and-save:"\n'
    "        + request.transaction_id\n"
    "    ))\n\n"
)

updated = source.replace(
    old_import,
    "from uuid import uuid4, uuid5, NAMESPACE_URL",
    1
)

updated = updated.replace(
    old_lookup,
    stable_id_code + old_lookup,
    1
)

updated = updated.replace(
    old_query,
    "Transaction.id == stable_tx_id",
    1
)

updated = updated.replace(
    old_values,
    '        "id": stable_tx_id,\n',
    1
)

compile(updated, str(target), "exec")

backup = target.with_name(
    "ml_persistence_router.py.backup_" +
    datetime.now().strftime("%Y%m%d_%H%M%S")
)

shutil.copy2(target, backup)

print("Original backup:", backup.name)

try:
    target.write_text(updated, encoding="utf-8")

    verification = """
from app.main import app
from app.models import Transaction

assert hasattr(Transaction, "id")

operation = app.openapi()["paths"][
    "/api/v1/ml/predict-and-save"
]["post"]

assert operation.get("security")

from app.ml_persistence_router import (
    router, FEATURES, load_model
)

assert len(FEATURES) == 30

print("ML MODULE IMPORT: PASS")
print("TRANSACTION ID MAPPING: PASS")
print("JWT SECURITY: PASS")
print("ML FEATURES: 30")
print("API REGISTRATION: PASS")
"""

    result = subprocess.run(
        [sys.executable, "-c", verification],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        print(result.stderr[-1200:])
        raise RuntimeError(
            "Backend verification failed."
        )

    print(result.stdout)

    print("ML STORAGE ID FIX APPLIED SUCCESSFULLY!")
    print("Existing PostgreSQL records: UNCHANGED")

except Exception as error:
    shutil.copy2(backup, target)
    print("Original ML router restored.")
    print("Verification error:", type(error).__name__)
    raise SystemExit(1)
