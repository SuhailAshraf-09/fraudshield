from getpass import getpass
from pathlib import Path
import json

from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.engine import URL

print("\nFRAUDSHIELD AI - CLEANUP ERROR DIAGNOSIS")

password = getpass("PostgreSQL app password: ")

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="fraudshield_app",
        password=password,
        host="127.0.0.1",
        port=5432,
        database="fraudshield_db"
    ),
    hide_parameters=True,
    connect_args={"connect_timeout": 10}
)

del password

stage = "Database Connection"

try:
    with engine.connect() as conn:

        conn.exec_driver_sql(
            "SET TRANSACTION READ ONLY"
        )

        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db",
            "fraudshield_app"
        ):
            raise RuntimeError("Unexpected database identity")

        print("Database Connection: PASS")

        stage = "Database Record Counts"

        counts = {}

        for table in (
            "transactions",
            "predictions",
            "alerts"
        ):
            counts[table] = conn.execute(
                text(
                    f"SELECT COUNT(*) FROM public.{table}"
                )
            ).scalar_one()

        print("Current Record Counts:", counts)

        stage = "Schema Reflection"

        metadata = MetaData()

        metadata.reflect(
            bind=conn,
            schema="public",
            only=[
                "transactions",
                "predictions",
                "alerts"
            ]
        )

        print("Schema Reflection: PASS")

        stage = "Test Report Comparison"

        report_path = (
            Path("reports")
            / "phase7"
            / "prediction_write_test.json"
        )

        if not report_path.is_file():
            raise RuntimeError(
                "Prediction write report missing"
            )

        report = json.loads(
            report_path.read_text(
                encoding="utf-8"
            )
        )

        print(
            "Counts Match Test Report:",
            counts == report.get("after")
        )

        print(
            "\nPOSTGRESQL CLEANUP DIAGNOSTIC PASSED"
        )

except Exception as error:
    print("\nDIAGNOSTIC FAILED")
    print("Failed Stage:", stage)
    print("Error Type:", type(error).__name__)

    original = getattr(error, "orig", error)
    sqlstate = getattr(
        original,
        "sqlstate",
        None
    )

    print("SQLSTATE:", sqlstate or "Unavailable")

    if sqlstate == "28P01":
        print("Reason: Incorrect PostgreSQL password.")
    elif sqlstate == "42501":
        print("Reason: Insufficient database permissions.")
    elif sqlstate in ("08001", "08006"):
        print("Reason: PostgreSQL connection problem.")
    else:
        print("Reason: Further review required.")

finally:
    engine.dispose()

print("\nNo database records modified.")
