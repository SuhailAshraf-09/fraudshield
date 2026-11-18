from getpass import getpass
from pathlib import Path
from datetime import datetime, timezone
import json

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

from app import database, models

print("\nFRAUDSHIELD AI - POSTGRESQL MIGRATION AUDIT")

sqlite_engine = database.engine

if sqlite_engine.dialect.name != "sqlite":
    raise SystemExit(
        "SAFETY STOP: Existing database is not SQLite."
    )

Base = getattr(database, "Base", None)

if Base is None:
    Base = getattr(models, "Base", None)

if Base is None:
    raise SystemExit("SAFETY STOP: ORM models unavailable.")

expected = set(Base.metadata.tables.keys())

password = getpass("PostgreSQL app password: ")

url = URL.create(
    "postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

del password

pg_engine = create_engine(
    url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

audit = {
    "generated_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "database": "fraudshield_db",
    "tables": {}
}

try:
    with sqlite_engine.connect() as sqlite_conn:
        with pg_engine.connect() as pg_conn:

            # PostgreSQL audit is read-only.
            pg_conn.exec_driver_sql(
                "SET TRANSACTION READ ONLY"
            )

            db_name, user_name = pg_conn.execute(
                text(
                    "SELECT current_database(), current_user"
                )
            ).one()

            if (
                db_name != "fraudshield_db"
                or user_name != "fraudshield_app"
            ):
                raise SystemExit(
                    "SAFETY STOP: Wrong database account."
                )

            sqlite_inspector = inspect(sqlite_conn)
            pg_inspector = inspect(pg_conn)

            sqlite_tables = set(
                sqlite_inspector.get_table_names()
            )

            pg_tables = set(
                pg_inspector.get_table_names(
                    schema="public"
                )
            )

            print("\nORM Tables:", sorted(expected))
            print("SQLite Tables:", sorted(sqlite_tables))
            print("PostgreSQL Tables:", sorted(pg_tables))

            if not (
                expected == sqlite_tables == pg_tables
            ):
                raise SystemExit(
                    "SAFETY STOP: Database table lists differ."
                )

            schema_matches = True
            pg_empty = True

            print("\nDATABASE RECORD COMPARISON")

            for table in sorted(expected):

                sqlite_name = (
                    sqlite_conn.dialect
                    .identifier_preparer.quote(table)
                )

                pg_name = (
                    pg_conn.dialect
                    .identifier_preparer.quote(table)
                )

                sqlite_count = sqlite_conn.execute(
                    text(
                        f"SELECT COUNT(*) FROM {sqlite_name}"
                    )
                ).scalar_one()

                pg_count = pg_conn.execute(
                    text(
                        f"SELECT COUNT(*) FROM public.{pg_name}"
                    )
                ).scalar_one()

                sqlite_columns = {
                    col["name"]
                    for col in sqlite_inspector.get_columns(
                        table
                    )
                }

                pg_columns = {
                    col["name"]
                    for col in pg_inspector.get_columns(
                        table,
                        schema="public"
                    )
                }

                sqlite_pk = set(
                    sqlite_inspector.get_pk_constraint(
                        table
                    ).get("constrained_columns") or []
                )

                pg_pk = set(
                    pg_inspector.get_pk_constraint(
                        table,
                        schema="public"
                    ).get("constrained_columns") or []
                )

                columns_match = (
                    sqlite_columns == pg_columns
                )

                primary_key_match = (
                    sqlite_pk == pg_pk
                )

                if not (
                    columns_match and primary_key_match
                ):
                    schema_matches = False

                if pg_count > 0:
                    pg_empty = False

                audit["tables"][table] = {
                    "sqlite_records": sqlite_count,
                    "postgresql_records": pg_count,
                    "columns_match": columns_match,
                    "primary_key_match": primary_key_match
                }

                print("\nTable:", table)
                print("SQLite Records:", sqlite_count)
                print("PostgreSQL Records:", pg_count)
                print("Columns Match:", columns_match)
                print("Primary Key Match:", primary_key_match)

            audit["basic_schema_match"] = schema_matches
            audit["postgresql_empty"] = pg_empty

            print("\nFINAL DATABASE AUDIT")

            if not schema_matches:
                print(
                    "SCHEMA REVIEW REQUIRED BEFORE MIGRATION"
                )
            elif not pg_empty:
                print(
                    "POSTGRESQL HAS EXISTING RECORDS - "
                    "REVIEW REQUIRED"
                )
            else:
                print(
                    "POSTGRESQL TABLES ARE EMPTY - "
                    "READY FOR NEXT MIGRATION CHECK"
                )

    output_dir = Path("reports") / "phase7"
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "postgres_pre_migration_audit.json"
    )

    output_file.write_text(
        json.dumps(audit, indent=2),
        encoding="utf-8"
    )

    print("\nAudit Report:", output_file)
    print("POSTGRESQL AUDIT COMPLETED")
    print("No database records modified.")

except SQLAlchemyError as error:
    print("Database audit failed.")
    print("Error Type:", type(error).__name__)
    raise SystemExit(1)

finally:
    pg_engine.dispose()
