
from getpass import getpass

from sqlalchemy import select
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

email = input("Admin email: ").strip().lower()

with SessionLocal() as db:
    user = db.scalar(
        select(User).where(
            User.email == email,
            User.role == "admin"
        )
    )

    if user is None:
        raise SystemExit("Admin account not found.")

    password = getpass("New strong password: ")
    confirm = getpass("Confirm new password: ")

    if password != confirm:
        raise SystemExit("Passwords do not match.")

    user.password_hash = hash_password(password)
    db.commit()

    print("Admin password updated successfully.")

