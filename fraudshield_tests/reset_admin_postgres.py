from getpass import getpass
from hmac import compare_digest

from sqlalchemy import (
    create_engine, select, update, func, text
)
from sqlalchemy.engine import URL

from app.models import Base
from app.security import hash_password, verify_password

print("\nFRAUDSHIELD AI - ADMIN PASSWORD RESET")

email = "admin@fraudshieldai.com"

new_password = getpass("New website admin password: ")
confirm_password = getpass("Confirm new admin password: ")

if not compare_digest(new_password, confirm_password):
    raise SystemExit("ERROR: Passwords do not match.")

if len(new_password) < 12:
    raise SystemExit(
        "ERROR: Use at least 12 characters."
    )

new_hash = hash_password(new_password)

if not verify_password(new_password, new_hash):
    raise SystemExit(
        "ERROR: Password hashing verification failed."
    )

del confirm_password

db_password = getpass("PostgreSQL app password: ")

if compare_digest(new_password, db_password):
    raise SystemExit(
        "ERROR: Use different website and database passwords."
    )

pg_engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="fraudshield_app",
        password=db_password,
        host="127.0.0.1",
        port=5432,
        database="fraudshield_db"
    ),
    connect_args={"connect_timeout": 10},
    hide_parameters=True
)

del db_password

users = Base.metadata.tables["users"]

try:
    with pg_engine.begin() as connection:

        identity = connection.execute(
            text("SELECT current_database(), current_user")
        ).one()

        if tuple(identity) != (
            "fraudshield_db", "fraudshield_app"
        ):
            raise RuntimeError("Incorrect database connection.")

        account = connection.execute(
            select(users.c.id, users.c.role).where(
                func.lower(users.c.email) == email
            )
        ).mappings().one_or_none()

        if account is None:
            raise RuntimeError("Admin account not found.")

        if str(account["role"]).lower() != "admin":
            raise RuntimeError("Account is not an admin.")

        result = connection.execute(
            update(users)
            .where(users.c.id == account["id"])
            .values(password_hash=new_hash)
        )

        if result.rowcount != 1:
            raise RuntimeError("Admin update failed.")

        stored_hash = connection.execute(
            select(users.c.password_hash).where(
                users.c.id == account["id"]
            )
        ).scalar_one()

        if not verify_password(
            new_password, stored_hash
        ):
            raise RuntimeError(
                "New password verification failed."
            )

    print("\nADMIN PASSWORD RESET SUCCESSFUL!")
    print("Admin account: VERIFIED")
    print("New password: VERIFIED")
    print("PostgreSQL update: COMMITTED")
    print("Other records: UNCHANGED")

except Exception as error:
    print("PASSWORD RESET FAILED")
    print("Error type:", type(error).__name__)
    print("No successful reset confirmed.")

finally:
    pg_engine.dispose()
    del new_password
