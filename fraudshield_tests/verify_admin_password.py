from getpass import getpass
from sqlalchemy import select, func

from app.database import engine, Base
from app.security import verify_password

print("\nFRAUDSHIELD AI - ADMIN PASSWORD VERIFICATION")

if engine.dialect.name != "sqlite":
    raise SystemExit(
        "Safety stop: Expected original SQLite database."
    )

users = Base.metadata.tables["users"]

email = input("Website admin email: ").strip().lower()
password = getpass("Website admin password: ")

with engine.connect() as connection:
    account = connection.execute(
        select(users).where(
            func.lower(users.c.email) == email
        )
    ).mappings().one_or_none()

if account is None:
    print("Admin Account Found: False")
    print("RESULT: ACCOUNT NOT FOUND")
else:
    print("Admin Account Found: True")
    print("Stored Role:", account["role"])

    try:
        verified = verify_password(
            password,
            account["password_hash"]
        )

        print("Password Verification:", bool(verified))

        if verified:
            print("RESULT: PASSWORD MATCHES STORED HASH")
            print("Next: Investigate login endpoint logic.")
        else:
            print("RESULT: PASSWORD DOES NOT MATCH")
            print("Next: Secure admin password reset.")

    except Exception as error:
        print("Verification Error:", type(error).__name__)
        print("RESULT: SECURITY FUNCTION REVIEW REQUIRED")

del password

print("\nNo passwords or hashes displayed.")
print("No database records modified.")
