import os
from getpass import getpass

import psycopg
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

print("\nFRAUDSHIELD AI - POSTGRESQL STARTUP DIAGNOSIS")

password = getpass("PostgreSQL app password: ")

settings = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "fraudshield_app",
    "dbname": "fraudshield_db",
    "password": password,
    "connect_timeout": 10
}

stage = "1 - Direct Psycopg Connection"
test_engine = None
app_engine = None

try:
    print("\nSTEP 1: Direct PostgreSQL connection")

    with psycopg.connect(**settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user"
            )
            identity = cursor.fetchone()

    if identity != ("fraudshield_db", "fraudshield_app"):
        raise RuntimeError("Unexpected PostgreSQL identity")

    print("Direct Psycopg: PASS")

    stage = "2 - SQLAlchemy Connection"

    print("\nSTEP 2: SQLAlchemy connection")

    url = URL.create(
        "postgresql+psycopg",
        username=settings["user"],
        password=password,
        host=settings["host"],
        port=settings["port"],
        database=settings["dbname"]
    )

    test_engine = create_engine(
        url,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 10}
    )

    with test_engine.connect() as conn:
        result = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

    if tuple(result) != (
        "fraudshield_db", "fraudshield_app"
    ):
        raise RuntimeError("Unexpected SQLAlchemy identity")

    print("SQLAlchemy: PASS")

    stage = "3 - FraudShield Database Configuration"

    print("\nSTEP 3: FraudShield database configuration")

    os.environ["FRAUDSHIELD_DATABASE_URL"] = (
        url.render_as_string(hide_password=False)
    )

    from app.database import engine as app_engine

    print("Selected engine:", app_engine.dialect.name)

    if app_engine.dialect.name != "postgresql":
        raise RuntimeError("PostgreSQL was not selected")

    with app_engine.connect() as conn:
        conn.execute(text("SELECT 1")).scalar_one()

    print("FraudShield Database Engine: PASS")

    stage = "4 - FastAPI Application Import"

    print("\nSTEP 4: FastAPI application import")

    from app.main import app

    paths = app.openapi().get("paths", {})

    for route in (
        "/api/v1/ml/predict",
        "/api/v1/ml/batch-predict",
        "/api/v1/ml/report-pdf"
    ):
        print(route, ":", route in paths)

    print("FastAPI Import: PASS")

    print("\nALL POSTGRESQL STARTUP CHECKS PASSED")

except Exception as error:
    print("\nDIAGNOSTIC FAILED")
    print("Failed Stage:", stage)
    print("Error Type:", type(error).__name__)

    original = getattr(error, "orig", error)
    sqlstate = getattr(original, "sqlstate", None)

    print("PostgreSQL SQLSTATE:", sqlstate or "Unavailable")

    if sqlstate == "28P01":
        print("Reason: PostgreSQL password rejected.")
    elif sqlstate == "3D000":
        print("Reason: Database does not exist.")
    elif sqlstate == "42501":
        print("Reason: Database permission denied.")
    elif sqlstate in ("08001", "08006"):
        print("Reason: Database connection failed.")
    else:
        print("Reason: Further inspection required.")

    print("No passwords or hashes displayed.")

finally:
    if test_engine is not None:
        test_engine.dispose()

    if app_engine is not None:
        app_engine.dispose()
