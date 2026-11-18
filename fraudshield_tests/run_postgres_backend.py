import os
from getpass import getpass

import uvicorn
from sqlalchemy import text
from sqlalchemy.engine import URL

print("\nFRAUDSHIELD AI - POSTGRESQL FASTAPI STARTUP")

password = getpass("PostgreSQL app password: ")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

os.environ["FRAUDSHIELD_DATABASE_URL"] = (
    database_url.render_as_string(
        hide_password=False
    )
)

del password
del database_url

try:
    # Import database only after configuring the URL.
    from app.database import engine

    if engine.dialect.name != "postgresql":
        raise RuntimeError(
            "SAFETY STOP: PostgreSQL engine not selected."
        )

    with engine.connect() as connection:
        identity = connection.execute(
            text(
                "SELECT current_database(), current_user"
            )
        ).one()

        if tuple(identity) != (
            "fraudshield_db",
            "fraudshield_app"
        ):
            raise RuntimeError(
                "SAFETY STOP: Incorrect database connection."
            )

        print("Database Engine: PostgreSQL")
        print("Database:", identity[0])
        print("User:", identity[1])

        for table in (
            "users",
            "transactions",
            "alerts",
            "predictions"
        ):
            count = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM public.{table}"
                )
            ).scalar_one()

            print(f"{table}: {count} records")

    from app.main import app

    paths = app.openapi()["paths"]

    required = [
        "/api/v1/ml/predict",
        "/api/v1/ml/batch-predict",
        "/api/v1/ml/report-pdf"
    ]

    for route in required:
        if route not in paths:
            raise RuntimeError(
                f"SAFETY STOP: Missing API route {route}"
            )

    print("\nAll three ML API routes: VERIFIED")
    print("PostgreSQL backend startup checks: PASSED")
    print("Starting FastAPI on http://127.0.0.1:8000")

except Exception as error:
    print("Backend startup verification: FAILED")
    print("Error type:", type(error).__name__)
    raise SystemExit(1)

# No reload process: keeps runtime credentials
# within this terminal's Python process.
uvicorn.run(
    app,
    host="127.0.0.1",
    port=8000,
    reload=False,
    log_level="info"
)
