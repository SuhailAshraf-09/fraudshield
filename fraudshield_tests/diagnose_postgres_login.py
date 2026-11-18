from getpass import getpass

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import URL

from app.database import engine as sqlite_engine
from app.models import Base

print("\nFRAUDSHIELD AI - LOGIN DATA DIAGNOSTIC")

if sqlite_engine.dialect.name != "sqlite":
    raise SystemExit(
        "Safety stop: SQLite source not detected."
    )

users = Base.metadata.tables["users"]

password = getpass("PostgreSQL app password: ")

pg_engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="fraudshield_app",
        password=password,
        host="127.0.0.1",
        port=5432,
        database="fraudshield_db"
    ),
    connect_args={"connect_timeout": 10},
    hide_parameters=True
)

del password

try:
    with sqlite_engine.connect() as src:
        source_rows = [
            dict(row)
            for row in src.execute(
                select(users)
            ).mappings()
        ]

    with pg_engine.connect() as dst:
        identity = dst.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise SystemExit("Unexpected database connection.")

        target_rows = [
            dict(row)
            for row in dst.execute(
                select(users)
            ).mappings()
        ]

    print("SQLite Users:", len(source_rows))
    print("PostgreSQL Users:", len(target_rows))

    original = {
        str(row["id"]): row
        for row in source_rows
    }

    migrated = {
        str(row["id"]): row
        for row in target_rows
    }

    print("User IDs Match:", set(original) == set(migrated))

    fields = [
        col.name
        for col in users.columns
        if any(
            part in col.name.lower()
            for part in (
                "email", "password", "role",
                "active", "enabled", "verified",
                "username"
            )
        )
    ]

    print("Authentication Fields:", fields)

    differences = []

    for user_id in sorted(set(original) & set(migrated)):
        for field in fields:
            if original[user_id][field] != migrated[user_id][field]:
                differences.append(
                    f"User {user_id}: {field}"
                )

    print(
        "Authentication Data Match:",
        len(differences) == 0
        and set(original) == set(migrated)
    )

    if differences:
        print("Differing Fields:", differences)
    else:
        print("No authentication-field differences detected.")

    admin_email = "admin@fraudshieldai.com"

    def admin_found(rows):
        return any(
            str(row.get("email", "")).strip().lower()
            == admin_email
            for row in rows
        )

    print("Admin In SQLite:", admin_found(source_rows))
    print("Admin In PostgreSQL:", admin_found(target_rows))

    print("\nLOGIN DATA DIAGNOSTIC COMPLETED")
    print("No passwords or hashes displayed.")
    print("No database records modified.")

finally:
    pg_engine.dispose()
