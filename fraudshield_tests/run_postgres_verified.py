import os
import sys
import socket
from getpass import getpass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import uvicorn

print("\nFRAUDSHIELD AI - VERIFIED POSTGRESQL STARTUP")

try:
    with socket.create_connection(
        ("127.0.0.1", 8000), timeout=1
    ):
        raise SystemExit(
            "SAFETY STOP: Port 8000 already occupied."
        )
except (ConnectionRefusedError, TimeoutError, OSError):
    pass

password = getpass("PostgreSQL fraudshield_app password: ")

url = URL.create(
    "postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

stage = "PostgreSQL connection"
engine = None

try:
    engine = create_engine(
        url,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 10}
    )

    with engine.connect() as conn:
        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

    if tuple(identity) != (
        "fraudshield_db", "fraudshield_app"
    ):
        raise RuntimeError("Incorrect database identity.")

    print("POSTGRESQL CONNECTION: PASS")
    print("Database:", identity[0])
    print("User:", identity[1])

except Exception as error:
    print("\nPOSTGRESQL CONNECTION: FAILED")
    print("Error Type:", type(error).__name__)

    original = getattr(error, "orig", error)
    detail = str(original).replace(
        password, "[REDACTED]"
    )

    if "password authentication failed" in detail.lower():
        print("REASON: PostgreSQL app password rejected.")
        print("Use the password that worked in psql.")
    else:
        print("Error Details:", detail[:500])

    raise SystemExit(1)

finally:
    if engine is not None:
        engine.dispose()

# Configure the database before importing the app.
os.environ["FRAUDSHIELD_DATABASE_URL"] = (
    url.render_as_string(hide_password=False)
)

del password
del url

stage = "FastAPI import and verification"

try:
    from app.database import engine as app_engine
    from app.main import app

    if app_engine.dialect.name != "postgresql":
        raise RuntimeError(
            "Backend is not using PostgreSQL."
        )

    with app_engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM public.users")
        ).scalar_one()

    print("FASTAPI DATABASE ENGINE: PostgreSQL")
    print("Users Found:", count)

    paths = app.openapi()["paths"]

    required = [
        "/api/v1/ml/predict",
        "/api/v1/ml/batch-predict",
        "/api/v1/ml/report-pdf",
        "/api/v1/ml/predict-and-save"
    ]

    for path in required:
        if path not in paths:
            raise RuntimeError("Missing ML API: " + path)

    print("ALL FOUR ML ENDPOINTS: VERIFIED")
    print("\nSTARTING POSTGRESQL FASTAPI SERVER")

except Exception as error:
    print("FASTAPI STARTUP CHECK: FAILED")
    print("Error Type:", type(error).__name__)
    raise SystemExit(1)

uvicorn.run(
    app,
    host="127.0.0.1",
    port=8000,
    reload=False,
    log_level="info"
)
