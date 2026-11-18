from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass
import json
import socket
import sqlite3

from sqlalchemy import (
    create_engine, inspect, select, func, text
)
from sqlalchemy.engine import URL

from app import database, models

print("\nFRAUDSHIELD AI - SQLITE TO POSTGRESQL MIGRATION")

# Ensure the main FastAPI server is stopped.
try:
    sock = socket.create_connection(
        ("127.0.0.1", 8000), timeout=1
    )
except OSError:
    pass
else:
    sock.close()
    raise SystemExit(
        "SAFETY STOP: Stop FastAPI on port 8000 first."
    )

if database.engine.dialect.name != "sqlite":
    raise SystemExit(
        "SAFETY STOP: Current backend is not using SQLite."
    )

Base = getattr(database, "Base", None)

if Base is None:
    Base = getattr(models, "Base", None)

if Base is None:
    raise SystemExit("SQLAlchemy Base not found.")

tables = list(Base.metadata.sorted_tables)

if not tables:
    raise SystemExit("No ORM tables found.")

sqlite_file = database.engine.url.database

if not sqlite_file or sqlite_file == ":memory:":
    raise SystemExit("File-based SQLite required.")

source_path = Path(sqlite_file).expanduser().resolve()

if not source_path.is_file():
    raise SystemExit("SQLite database file not found.")

# Create a consistent private SQLite backup.
backup_dir = Path.home() / "FraudShield_Private_Backups"
backup_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now(timezone.utc).strftime(
    "%Y%m%d_%H%M%S_%f"
)

backup_file = backup_dir / (
    f"pre_migration_{timestamp}.sqlite3"
)

src = sqlite3.connect(
    source_path.as_uri() + "?mode=ro",
    uri=True,
    timeout=30
)

dst = sqlite3.connect(str(backup_file))

try:
    src.backup(dst)

    if dst.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0] != "ok":
        raise SystemExit(
            "SAFETY STOP: Backup integrity check failed."
        )

    if dst.execute(
        "PRAGMA foreign_key_check"
    ).fetchone() is not None:
        raise SystemExit(
            "SAFETY STOP: SQLite foreign key violations."
        )
finally:
    dst.close()
    src.close()

print("SQLite backup verified:", backup_file)

snapshot_engine = create_engine(
    URL.create("sqlite", database=str(backup_file))
)

password = getpass("PostgreSQL app password: ")

pg_engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="fraudshield_app",
        password=password,
        host="127.0.0.1",
        port=5432,
        database="fraudshield_db"
    ),
    connect_args={"connect_timeout": 10},
    pool_pre_ping=True,
    hide_parameters=True
)

del password

try:
    src_info = inspect(snapshot_engine)
    pg_info = inspect(pg_engine)

    expected = {t.name for t in tables}

    if expected != set(src_info.get_table_names()):
        raise RuntimeError("SQLite table list mismatch.")

    if expected != set(
        pg_info.get_table_names(schema="public")
    ):
        raise RuntimeError("PostgreSQL table list mismatch.")

    print("\nSCHEMA VERIFICATION")

    def foreign_key_signature(fks):
        return {
            (
                tuple(fk["constrained_columns"]),
                fk["referred_table"],
                tuple(fk["referred_columns"])
            )
            for fk in fks
        }

    for table in tables:
        name = table.name

        source_columns = {
            c["name"]
            for c in src_info.get_columns(name)
        }

        target_columns = {
            c["name"]
            for c in pg_info.get_columns(
                name, schema="public"
            )
        }

        if source_columns != target_columns:
            raise RuntimeError(
                f"Column mismatch: {name}"
            )

        source_pk = set(
            src_info.get_pk_constraint(
                name
            ).get("constrained_columns") or []
        )

        target_pk = set(
            pg_info.get_pk_constraint(
                name, schema="public"
            ).get("constrained_columns") or []
        )

        if source_pk != target_pk:
            raise RuntimeError(
                f"Primary key mismatch: {name}"
            )

        source_fks = foreign_key_signature(
            src_info.get_foreign_keys(name)
        )

        target_fks = foreign_key_signature(
            pg_info.get_foreign_keys(
                name, schema="public"
            )
        )

        if source_fks != target_fks:
            raise RuntimeError(
                f"Foreign key mismatch: {name}"
            )

        print("Schema OK:", name)

    counts = {}

    with snapshot_engine.connect() as source:
        with pg_engine.connect() as destination:

            identity = destination.execute(
                text(
                    "SELECT current_database(), current_user"
                )
            ).one()

            if tuple(identity) != (
                "fraudshield_db", "fraudshield_app"
            ):
                raise RuntimeError(
                    "Incorrect PostgreSQL target."
                )

            print("\nPRE-MIGRATION RECORD COUNTS")

            for table in tables:
                source_count = source.execute(
                    select(func.count()).select_from(table)
                ).scalar_one()

                target_count = destination.execute(
                    select(func.count()).select_from(table)
                ).scalar_one()

                print(
                    f"{table.name}: "
                    f"SQLite={source_count}, "
                    f"PostgreSQL={target_count}"
                )

                if target_count != 0:
                    raise RuntimeError(
                        f"Destination table is not empty: "
                        f"{table.name}"
                    )

                counts[table.name] = source_count

    print("\nAll preliminary checks completed.")
    print("No records have been transferred yet.")

    confirmation = input(
        "Type MIGRATE to transfer data, "
        "or press Enter to cancel: "
    ).strip()

    if confirmation != "MIGRATE":
        raise SystemExit(
            "Migration cancelled. No records transferred."
        )

    print("\nSTARTING DATABASE MIGRATION")

    # All record inserts use one PostgreSQL transaction.
    with snapshot_engine.connect() as source:
        with pg_engine.begin() as destination:

            for table in tables:
                current = destination.execute(
                    select(func.count()).select_from(table)
                ).scalar_one()

                if current != 0:
                    raise RuntimeError(
                        f"Destination changed: {table.name}"
                    )

            for table in tables:
                rows = source.execute(
                    select(table)
                ).mappings()

                copied = 0

                while True:
                    batch = rows.fetchmany(200)

                    if not batch:
                        break

                    destination.execute(
                        table.insert(),
                        [dict(row) for row in batch]
                    )

                    copied += len(batch)

                actual = destination.execute(
                    select(func.count()).select_from(table)
                ).scalar_one()

                if (
                    copied != counts[table.name]
                    or actual != counts[table.name]
                ):
                    raise RuntimeError(
                        f"Record count mismatch: {table.name}"
                    )

                print(
                    f"Migrated {table.name}: {copied} records"
                )

            # Synchronize generated primary-key sequences.
            for table in tables:
                keys = list(table.primary_key.columns)

                if len(keys) != 1:
                    continue

                pk = keys[0]

                sequence = destination.execute(
                    text("""
                        SELECT pg_get_serial_sequence(
                            :table_name, :column_name
                        )
                    """),
                    {
                        "table_name": f"public.{table.name}",
                        "column_name": pk.name
                    }
                ).scalar_one_or_none()

                if sequence:
                    maximum = destination.execute(
                        select(func.max(pk))
                    ).scalar_one()

                    if maximum is not None:
                        destination.execute(
                            text("""
                                SELECT setval(
                                    CAST(:sequence AS regclass),
                                    :value,
                                    true
                                )
                            """),
                            {
                                "sequence": sequence,
                                "value": int(maximum)
                            }
                        )

    print("\nDATABASE TRANSACTION COMMITTED")

    with pg_engine.connect() as destination:
        final_counts = {
            table.name: destination.execute(
                select(func.count()).select_from(table)
            ).scalar_one()
            for table in tables
        }

    if final_counts != counts:
        raise RuntimeError(
            "Post-commit verification failed."
        )

    report_dir = Path("reports") / "phase7"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = (
        report_dir / "postgres_migration_result.json"
    )

    report_file.write_text(
        json.dumps({
            "status": "passed",
            "backup": str(backup_file),
            "source_counts": counts,
            "postgresql_counts": final_counts,
            "fastapi_switched": False
        }, indent=2),
        encoding="utf-8"
    )

    print("\nPOSTGRESQL DATA MIGRATION SUCCESSFUL!")
    print("All record counts verified.")
    print("Report:", report_file)
    print("Original SQLite database unchanged.")
    print("FastAPI PostgreSQL switching: PENDING")

except Exception as error:
    print("\nMIGRATION STOPPED")
    print("Error Type:", type(error).__name__)
    print("Details:", str(error))
    print(
        "Do not rerun until PostgreSQL counts "
        "have been checked."
    )
    raise SystemExit(1)

finally:
    snapshot_engine.dispose()
    pg_engine.dispose()
