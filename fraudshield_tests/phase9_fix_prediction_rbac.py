import ast
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "app" / "main.py"

print("\nFRAUDSHIELD AI - PREDICTION RBAC SECURITY FIX")

source = MAIN.read_text(encoding="utf-8-sig")
tree = ast.parse(source)

matches = []

for node in tree.body:
    if not isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef)
    ):
        continue

    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue

        if any(
            isinstance(arg, ast.Constant)
            and arg.value == "/api/v1/predictions"
            for arg in decorator.args
        ):
            matches.append(node)

if len(matches) != 1:
    raise SystemExit(
        "SAFETY STOP: Expected exactly one prediction handler."
    )

handler = matches[0]
lines = source.splitlines(keepends=True)

old = "user: User = Depends(current_user)"
new = "user: User = Depends(reviewer_or_admin)"

header = lines[handler.lineno - 1]

if new in header:
    print("Role security already present. No changes made.")
    raise SystemExit(0)

if header.count(old) != 1:
    raise SystemExit(
        "SAFETY STOP: Unexpected handler signature."
    )

lines[handler.lineno - 1] = header.replace(old, new, 1)

# Add security import after any module docstring
# and Python future imports.
if not any(
    isinstance(n, ast.ImportFrom)
    and n.module == "app.security"
    and any(
        alias.name == "reviewer_or_admin"
        for alias in n.names
    )
    for n in tree.body
):
    insert_at = 0

    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        insert_at = tree.body[0].end_lineno

    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "__future__"
        ):
            insert_at = max(insert_at, node.end_lineno)

    lines.insert(
        insert_at,
        "from app.security import reviewer_or_admin\n"
    )

updated = "".join(lines)

compile(updated, str(MAIN), "exec")

backup = MAIN.with_name(
    "main.py.backup_rbac_"
    + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
)

shutil.copy2(MAIN, backup)

print("Backup created:", backup.name)

try:
    MAIN.write_text(updated, encoding="utf-8")

    verification = """
from app.main import app
from app.security import current_user, reviewer_or_admin
from app.database import get_db
from app.models import User
from fastapi.testclient import TestClient

routes = [
    r for r in app.routes
    if getattr(r, "path", None) == "/api/v1/predictions"
    and "POST" in getattr(r, "methods", set())
]

assert len(routes) == 1

assert any(
    d.call is reviewer_or_admin
    for d in routes[0].dependant.dependencies
), "Role guard not installed"

assert not app.dependency_overrides

try:
    app.dependency_overrides[get_db] = lambda: None

    with TestClient(
        app, raise_server_exceptions=False
    ) as client:

        for role, expected in (
            ("admin", 422),
            ("reviewer", 422),
            ("viewer", 403)
        ):
            user = User(
                email="test-" + role + "@example.invalid",
                password_hash="synthetic-only",
                role=role
            )

            def fake_user():
                return user

            app.dependency_overrides[current_user] = fake_user

            response = client.post(
                "/api/v1/predictions",
                json={}
            )

            print(role, response.status_code)

            assert response.status_code == expected

finally:
    app.dependency_overrides.clear()

print("PREDICTION ROLE GUARD: PASS")
print("ADMIN / REVIEWER / VIEWER: PASS")
print("NO VALID WRITE REQUESTS SUBMITTED")
"""

    result = subprocess.run(
        [sys.executable, "-c", verification],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=45
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr[-1200:])
        raise RuntimeError("Security verification failed.")

    print("\nLEGACY PREDICTION RBAC FIX SUCCESSFUL!")
    print("Existing database records: UNCHANGED")

except Exception as error:
    shutil.copy2(backup, MAIN)
    print("Verification failed. Original main.py restored.")
    print("Error type:", type(error).__name__)
    raise SystemExit(1)