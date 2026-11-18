from pathlib import Path
from getpass import getpass
import json
import re

from sqlalchemy import (
    create_engine, MetaData, select,
    or_, String, Text, text
)
from sqlalchemy.engine import URL

print("\nFRAUDSHIELD AI - PREDICTION RELATIONSHIP TEST")

report_path = Path(
    "reports/phase7/prediction_write_test.json"
)

if not report_path.is_file():
    raise SystemExit("Prediction test report missing.")

report = json.loads(
    report_path.read_text(encoding="utf-8")
)

test_id = report.get("test_transaction_id", "")

if (
    not report.get("checks_passed")
    or not re.fullmatch(r"FSTEST[0-9a-f]{12}", test_id)
):
    raise SystemExit("Safety stop: Invalid test report.")

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

try:
    metadata = MetaData()

    metadata.reflect(
        bind=engine,
        schema="public",
        only=["transactions", "predictions", "alerts"]
    )

    transactions = metadata.tables["public.transactions"]
    predictions = metadata.tables["public.predictions"]
    alerts = metadata.tables["public.alerts"]

    with engine.connect() as conn:
        conn.exec_driver_sql("SET TRANSACTION READ ONLY")

        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong PostgreSQL database.")

        text_columns = [
            c for c in transactions.columns
            if isinstance(c.type, (String, Text))
        ]

        if not text_columns:
            raise RuntimeError(
                "No transaction identifier columns found."
            )

        matches = conn.execute(
            select(transactions).where(
                or_(*[
                    c == test_id for c in text_columns
                ])
            )
        ).mappings().all()

        print("Test Transaction Found:", len(matches))

        if len(matches) != 1:
            print(
                "Relationship review required. "
                "No cleanup performed."
            )
            raise SystemExit(1)

        tx = matches[0]

        for name, table in (
            ("predictions", predictions),
            ("alerts", alerts)
        ):
            links = [
                fk for fk in table.foreign_keys
                if fk.column.table.name == "transactions"
            ]

            if not links:
                print(name, "has no declared transaction FK")
                continue

            conditions = [
                fk.parent == tx[fk.column.name]
                for fk in links
            ]

            related = conn.execute(
                select(table).where(or_(*conditions))
            ).mappings().all()

            print(
                "Linked", name,
                "records:", len(related)
            )

    print("\nRELATIONSHIP INSPECTION COMPLETED")
    print("No records modified or deleted.")

finally:
    engine.dispose()
