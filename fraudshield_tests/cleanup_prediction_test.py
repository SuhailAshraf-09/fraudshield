import json
import re
from pathlib import Path
from getpass import getpass

from sqlalchemy import (
    create_engine, MetaData, select,
    delete, func, or_, String, Text, text
)
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "phase7" / "prediction_write_test.json"

print("\nFRAUDSHIELD AI - SAFE TEST DATA CLEANUP")

if not REPORT.is_file():
    raise SystemExit("SAFETY STOP: Test report missing.")

report = json.loads(REPORT.read_text(encoding="utf-8"))

test_id = report.get("test_transaction_id", "")

if not re.fullmatch(r"FSTEST[0-9a-f]{12}", test_id):
    raise SystemExit("SAFETY STOP: Invalid test ID.")

if report.get("checks_passed") is not True:
    raise SystemExit("SAFETY STOP: Original test not passed.")

expected_diff = {
    "transactions": 1,
    "predictions": 1,
    "alerts": 0
}

if report.get("record_differences") != expected_diff:
    raise SystemExit("SAFETY STOP: Unexpected write counts.")

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

    tx = metadata.tables["public.transactions"]
    pred = metadata.tables["public.predictions"]
    alert = metadata.tables["public.alerts"]

    tables = {
        "transactions": tx,
        "predictions": pred,
        "alerts": alert
    }

    def get_counts(conn):
        return {
            name: conn.execute(
                select(func.count()).select_from(table)
            ).scalar_one()
            for name, table in tables.items()
        }

    with engine.begin() as conn:
        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong PostgreSQL target.")

        before = get_counts(conn)
        print("Current counts:", before)

        if before != report.get("after"):
            raise RuntimeError(
                "Database counts changed. Cleanup stopped."
            )

        text_columns = [
            col for col in tx.columns
            if isinstance(col.type, (String, Text))
        ]

        matches = conn.execute(
            select(tx).where(
                or_(*[col == test_id for col in text_columns])
            ).with_for_update()
        ).mappings().all() if text_columns else []

        if len(matches) != 1:
            raise RuntimeError(
                "Exactly one test transaction required."
            )

        transaction = matches[0]

        pred_fks = [
            fk for fk in pred.foreign_keys
            if fk.column.table.name == "transactions"
        ]

        alert_fks = [
            fk for fk in alert.foreign_keys
            if fk.column.table.name == "transactions"
        ]

        if len(pred_fks) != 1 or len(alert_fks) != 1:
            raise RuntimeError("Foreign key review required.")

        pfk = pred_fks[0]
        afk = alert_fks[0]

        linked_predictions = conn.execute(
            select(pred).where(
                pfk.parent == transaction[pfk.column.name]
            ).with_for_update()
        ).mappings().all()

        linked_alerts = conn.execute(
            select(alert).where(
                afk.parent == transaction[afk.column.name]
            )
        ).mappings().all()

        print("Test Transactions:", len(matches))
        print("Linked Predictions:", len(linked_predictions))
        print("Linked Alerts:", len(linked_alerts))

        if len(linked_predictions) != 1 or linked_alerts:
            raise RuntimeError(
                "Unexpected linked records. No deletion."
            )

        tx_keys = list(tx.primary_key.columns)
        pred_keys = list(pred.primary_key.columns)

        if len(tx_keys) != 1 or len(pred_keys) != 1:
            raise RuntimeError("Primary key review required.")

        confirm = input(
            "Type CLEANUP to delete these 2 test records: "
        ).strip()

        if confirm != "CLEANUP":
            raise RuntimeError("Cleanup cancelled.")

        pk_pred = pred_keys[0]
        pk_tx = tx_keys[0]

        deleted_pred = conn.execute(
            delete(pred).where(
                pk_pred == linked_predictions[0][pk_pred.name]
            )
        )

        deleted_tx = conn.execute(
            delete(tx).where(
                pk_tx == transaction[pk_tx.name]
            )
        )

        if (
            deleted_pred.rowcount != 1
            or deleted_tx.rowcount != 1
        ):
            raise RuntimeError("Unexpected deletion count.")

        after = get_counts(conn)

        if after != report.get("before"):
            raise RuntimeError(
                "Original counts not restored. Rolling back."
            )

    print("\nDATABASE CLEANUP COMMITTED")

    with engine.connect() as conn:
        verified = get_counts(conn)

    if verified != report["before"]:
        raise RuntimeError("Final count verification failed.")

    output = ROOT / "reports" / "phase7" / "prediction_cleanup_result.json"

    output.write_text(
        json.dumps({
            "cleanup_status": "passed",
            "test_transaction_id": test_id,
            "remaining_counts": verified
        }, indent=2),
        encoding="utf-8"
    )

    print("Original record counts restored: PASS")
    print("TEST RECORD CLEANUP SUCCESSFUL!")

except Exception as error:
    print("SAFETY STOP:", type(error).__name__)
    print("Do not retry until database state is reviewed.")
    raise SystemExit(1)

finally:
    engine.dispose()
