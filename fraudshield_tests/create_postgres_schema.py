from getpass import getpass

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

from app import database, models

print("\nFRAUDSHIELD AI - POSTGRESQL TABLE SETUP")

# Existing SQLite database safety check
sqlite_engine = database.engine

if sqlite_engine.dialect.name != "sqlite":
    raise SystemExit(
        "Safety stop: Existing database is not SQLite."
    )

Base = getattr(database, "Base", None)

if Base is None:
    Base = getattr(models, "Base", None)

if Base is None:
    raise SystemExit("SQLAlchemy Base not found.")

model_tables = set(Base.metadata.tables.keys())
sqlite_tables = set(
    inspect(sqlite_engine).get_table_names()
)

print("Model Tables:", sorted(model_tables))
print("SQLite Tables:", sorted(sqlite_tables))

if not model_tables or model_tables != sqlite_tables:
    raise SystemExit(
        "Safety stop: SQLite schema differs from models."
    )

# Secure PostgreSQL connection
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
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

try:
    with engine.connect() as conn:
        db, user = conn.execute(
            text(
                "SELECT current_database(), current_user"
            )
        ).one()

    if db != "fraudshield_db" or user != "fraudshield_app":
        raise SystemExit(
            "Safety stop: Incorrect PostgreSQL connection."
        )

    existing = set(
        inspect(engine).get_table_names(schema="public")
    )

    print("Existing PostgreSQL Tables:", sorted(existing))

    if existing:
        raise SystemExit(
            "Safety stop: PostgreSQL already contains tables. "
            "No changes made."
        )

    # Transactional schema creation
    with engine.begin() as connection:
        Base.metadata.create_all(bind=connection)

    inspector = inspect(engine)
    created = set(
        inspector.get_table_names(schema="public")
    )

    print("\nPOSTGRESQL TABLES")

    for table_name in sorted(created):
        print("Created:", table_name)

    if created != model_tables:
        raise SystemExit(
            "Schema verification failed. Review required."
        )

    print("\nPOSTGRESQL TABLE SETUP SUCCESSFUL!")
    print("SQLite database preserved.")
    print("Data migration not yet performed.")

finally:
    engine.dispose()
