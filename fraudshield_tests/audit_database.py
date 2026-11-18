from pathlib import Path
from datetime import datetime, timezone
import sqlite3

from app import database, models

ROOT = Path(__file__).resolve().parent.parent
engine = database.engine

print("\nFRAUDSHIELD AI - DATABASE BACKUP AND AUDIT")

if engine.dialect.name != "sqlite":
    raise SystemExit(
        "Safety stop: Current database is not SQLite."
    )

db_name = engine.url.database

if not db_name or db_name == ":memory:":
    raise SystemExit("Safety stop: File-based SQLite not found.")

source_path = Path(db_name)

if not source_path.is_absolute():
    source_path = ROOT / source_path

source_path = source_path.resolve()

if not source_path.is_file():
    raise SystemExit(
        f"Safety stop: Database file missing: {source_path}"
    )

print("Current Database: SQLite")
print("SQLite Path:", source_path)

# Backups are kept outside the Git project.
backup_dir = Path.home() / "FraudShield_Private_Backups"
backup_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now(timezone.utc).strftime(
    "%Y%m%d_%H%M%S_%f"
)

backup_path = backup_dir / f"fraudshield_{timestamp}.sqlite3"

# SQLite online backup provides a consistent snapshot.
source_connection = sqlite3.connect(
    source_path.as_uri() + "?mode=ro",
    uri=True,
    timeout=30
)

backup_connection = sqlite3.connect(str(backup_path))

try:
    source_connection.backup(backup_connection)
finally:
    backup_connection.close()
    source_connection.close()

# Verify the copied database and inspect its contents.
with sqlite3.connect(str(backup_path)) as connection:
    integrity = connection.execute(
        "PRAGMA quick_check"
    ).fetchone()[0]

    if integrity != "ok":
        raise SystemExit(
            f"Backup integrity check failed: {integrity}"
        )

    tables = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    print("\nBACKUP DETAILS")
    print("Backup Path:", backup_path)
    print("Integrity:", integrity)
    print("Backup Size:", backup_path.stat().st_size, "bytes")

    print("\nEXISTING SQLITE TABLES")

    for (table_name,) in tables:
        safe_name = table_name.replace('"', '""')

        count = connection.execute(
            f'SELECT COUNT(*) FROM "{safe_name}"'
        ).fetchone()[0]

        columns = connection.execute(
            f'PRAGMA table_info("{safe_name}")'
        ).fetchall()

        column_names = [column[1] for column in columns]

        print(f"\nTable: {table_name}")
        print(f"Rows: {count}")
        print("Columns:", ", ".join(column_names))

print("\nSQLALCHEMY MODEL TABLES")

base = getattr(database, "Base", None)

if base is None:
    base = getattr(models, "Base", None)

if base is not None:
    for table in base.metadata.sorted_tables:
        print("Model Table:", table.name)
else:
    print("Base metadata not found; manual review needed.")

print("\nDATABASE BACKUP AND AUDIT COMPLETED")
print("Existing SQLite database was not modified.")
