from getpass import getpass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

print("\nFRAUDSHIELD AI - POSTGRESQL CONNECTION TEST")

password = getpass("PostgreSQL app password: ")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username="fraudshield_app",
    password=password,
    host="127.0.0.1",
    port=5432,
    database="fraudshield_db"
)

try:
    engine = create_engine(
        database_url,
        poolclass=NullPool,
        connect_args={"connect_timeout": 10}
    )

    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    current_database() AS database_name,
                    current_user AS database_user
            """)
        ).mappings().one()

        print("Connection Status: SUCCESS")
        print("Database:", result["database_name"])
        print("User:", result["database_user"])
        print("SQLAlchemy + Psycopg: WORKING")

    engine.dispose()

except Exception as error:
    print("Connection Status: FAILED")
    print("Error Type:", type(error).__name__)
    raise SystemExit(1)
