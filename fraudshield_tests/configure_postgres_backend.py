import ast
import os
import re
import shutil
import subprocess
import sys

from pathlib import Path
from datetime import datetime
from getpass import getpass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "app" / "database.py"

print("\nFRAUDSHIELD AI - POSTGRESQL BACKEND CONFIGURATION")

if not DB_FILE.is_file():
    raise SystemExit("SAFETY STOP: database.py missing.")

source = DB_FILE.read_text(encoding="utf-8-sig")

if "FRAUDSHIELD_DATABASE_URL" in source:
    raise SystemExit(
        "SAFETY STOP: PostgreSQL override already exists."
    )

tree = ast.parse(source)

engine_nodes = [
    node for node in tree.body
    if isinstance(node, ast.Assign)
    and any(
        isinstance(target, ast.Name)
        and target.id == "engine"
        for target in node.targets
    )
]

if len(engine_nodes) != 1:
    raise SystemExit(
        "SAFETY STOP: Engine configuration needs manual review."
    )

node = engine_nodes[0]

if not (
    isinstance(node.value, ast.Call)
    and isinstance(node.value.func, ast.Name)
    and node.value.func.id == "create_engine"
):
    raise SystemExit(
        "SAFETY STOP: Unsupported engine configuration."
    )

lines = source.splitlines(keepends=True)
old_assignment = "".join(
    lines[node.lineno - 1:node.end_lineno]
)

if not re.match(
    r"^\s*engine\s*=\s*create_engine\s*\(",
    old_assignment
):
    raise SystemExit(
        "SAFETY STOP: Engine assignment needs review."
    )

print("Existing SQLAlchemy engine detected.")
print("Original database file: preserved until verification.")

password = getpass("PostgreSQL app password: ")

pg_url = URL.create(
    "postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

del password

# Verify PostgreSQL before changing application code.
check_engine = create_engine(
    pg_url,
    connect_args={"connect_timeout": 10},
    hide_parameters=True
)

try:
    with check_engine.connect() as conn:
        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong PostgreSQL database.")

        for table in (
            "users", "transactions",
            "alerts", "predictions"
        ):
            count = conn.execute(
                text(f"SELECT COUNT(*) FROM public.{table}")
            ).scalar_one()

            print(f"PostgreSQL {table}: {count} records")

finally:
    check_engine.dispose()

print("PostgreSQL connection: VERIFIED")

original_expression = ast.unparse(node.value)

replacement = f'''
# FRAUDSHIELD POSTGRESQL CONFIGURATION V1
import os as _fraudshield_os
from sqlalchemy import create_engine as _fraudshield_engine_factory

def _fraudshield_initialize_engine():
    override = _fraudshield_os.environ.get(
        "FRAUDSHIELD_DATABASE_URL"
    )

    if override:
        if not override.startswith("postgresql+psycopg://"):
            raise RuntimeError(
                "Unsupported FraudShield database driver."
            )

        return _fraudshield_engine_factory(
            override,
            pool_pre_ping=True,
            hide_parameters=True,
            connect_args={{"connect_timeout": 10}}
        )

    return {original_expression}

engine = _fraudshield_initialize_engine()
'''

patched = (
    "".join(lines[:node.lineno - 1])
    + replacement
    + "".join(lines[node.end_lineno:])
)

compile(patched, str(DB_FILE), "exec")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = DB_FILE.with_name(
    f"database.py.backup_{timestamp}"
)

shutil.copy2(DB_FILE, backup)
print("Backup created:", backup.name)

try:
    DB_FILE.write_text(patched, encoding="utf-8")

    clean_env = os.environ.copy()
    clean_env.pop("FRAUDSHIELD_DATABASE_URL", None)

    sqlite_test = subprocess.run(
        [
            sys.executable, "-c",
            "from app.database import engine; "
            "assert engine.dialect.name == 'sqlite'; "
            "print('SQLite fallback: PASS')"
        ],
        cwd=ROOT,
        env=clean_env,
        capture_output=True,
        text=True
    )

    if sqlite_test.returncode != 0:
        raise RuntimeError("SQLite fallback verification failed.")

    print(sqlite_test.stdout.strip())

    pg_env = clean_env.copy()
    pg_env["FRAUDSHIELD_DATABASE_URL"] = (
        pg_url.render_as_string(hide_password=False)
    )

    pg_test = subprocess.run(
        [
            sys.executable, "-c",
            "from app.database import engine; "
            "assert engine.dialect.name == 'postgresql'; "
            "print('PostgreSQL override: PASS')"
        ],
        cwd=ROOT,
        env=pg_env,
        capture_output=True,
        text=True
    )

    if pg_test.returncode != 0:
        raise RuntimeError(
            "PostgreSQL override verification failed."
        )

    print(pg_test.stdout.strip())

    print("\nDATABASE CONFIGURATION SUCCESSFUL!")
    print("Existing SQLite fallback: PRESERVED")
    print("PostgreSQL override: AVAILABLE")
    print("No database records modified.")
    print("FastAPI PostgreSQL startup: NEXT STEP")

except Exception as error:
    shutil.copy2(backup, DB_FILE)
    print("Original database.py restored.")
    print("Error:", type(error).__name__)
    raise SystemExit(1)
