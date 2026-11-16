"""Create initial admin in a local terminal: python -m app.create_admin"""
import getpass
from sqlalchemy import select
from .database import Base, SessionLocal, engine
from .models import User
from .security import hash_password


def main():
    Base.metadata.create_all(bind=engine)  # Prototype only; migrations for production.
    email = input("Admin email: ").strip().lower()
    if not email or "@" not in email:
        raise ValueError("Enter a valid email")
    password = getpass.getpass("Choose a strong admin password (12+ characters): ")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)):
            raise ValueError("An account with that email already exists")
        db.add(User(email=email, role="admin", password_hash=hash_password(password)))
        db.commit()
    print("Admin created. Do not share credentials.")


if __name__ == "__main__":
    main()
