from getpass import getpass
import secrets

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

print("\nFRAUDSHIELD AI - POSTGRESQL PERSISTENCE TEST")

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

engine = create_engine(
    url,
    poolclass=NullPool,
    hide_parameters=True,
    connect_args={"connect_timeout": 10}
)

table = "public.fraudshield_persistence_probe"
record_id = secrets.token_hex(16)
record_value = "FraudShield AI persistence verified"

created = False
verified = False
cleaned = False
stage = "connection"

try:
    with engine.begin() as conn:
        identity = conn.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Wrong database connection")

        existing = conn.execute(
            text(
                "SELECT to_regclass("
                "'public.fraudshield_persistence_probe')"
            )
        ).scalar_one_or_none()

        if existing is not None:
            raise RuntimeError(
                "Test table already exists. Safety stop."
            )

        stage = "write"

        conn.execute(text("""
            CREATE TABLE public.fraudshield_persistence_probe (
                record_id VARCHAR(32) PRIMARY KEY,
                record_value TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(
            text("""
                INSERT INTO public.fraudshield_persistence_probe
                    (record_id, record_value)
                VALUES (:record_id, :record_value)
            """),
            {
                "record_id": record_id,
                "record_value": record_value
            }
        )

    created = True
    print("Database Write: PASS")
    print("Transaction Commit: PASS")

    # NullPool ensures a new database connection.
    stage = "read"

    with engine.connect() as conn:
        saved_value = conn.execute(
            text("""
                SELECT record_value
                FROM public.fraudshield_persistence_probe
                WHERE record_id = :record_id
            """),
            {"record_id": record_id}
        ).scalar_one_or_none()

    if saved_value != record_value:
        raise RuntimeError("Saved record verification failed")

    verified = True
    print("New Connection Read: PASS")
    print("Data Persistence Across Connections: PASS")

except Exception as error:
    print("TEST FAILED")
    print("Failed Stage:", stage)
    print("Error Type:", type(error).__name__)

finally:
    if created:
        try:
            with engine.begin() as conn:
                rows = conn.execute(
                    text("""
                        SELECT record_id
                        FROM public.fraudshield_persistence_probe
                    """)
                ).scalars().all()

                if rows != [record_id]:
                    raise RuntimeError(
                        "Unexpected test table contents"
                    )

                conn.execute(text(
                    "DROP TABLE public.fraudshield_persistence_probe"
                ))

            cleaned = True
            print("Temporary Test Table Cleanup: PASS")

        except Exception as cleanup_error:
            print("Cleanup requires review.")
            print(
                "Cleanup Error Type:",
                type(cleanup_error).__name__
            )

    engine.dispose()

if not (verified and cleaned):
    raise SystemExit("PERSISTENCE TEST NOT FULLY PASSED")

print("\nPOSTGRESQL PERSISTENCE TEST PASSED!")
print("Application tables: UNCHANGED")
