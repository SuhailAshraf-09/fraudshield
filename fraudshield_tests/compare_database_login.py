from getpass import getpass

import httpx
from fastapi.testclient import TestClient

from app.database import engine

print("\nFRAUDSHIELD AI - DUAL DATABASE LOGIN TEST")

if engine.dialect.name != "sqlite":
    raise SystemExit(
        "Safety stop: Local comparison must use SQLite."
    )

from app.main import app

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

credentials = {
    "email": email,
    "password": password
}

endpoint = "/api/v1/auth/login"

try:
    # Test original SQLite application locally.
    with TestClient(app) as client:
        sqlite_response = client.post(
            endpoint,
            json=credentials
        )

    print(
        "SQLite Login Status:",
        sqlite_response.status_code
    )

    # Test running PostgreSQL FastAPI server.
    with httpx.Client(timeout=15) as client:
        postgres_response = client.post(
            "http://127.0.0.1:8000" + endpoint,
            json=credentials
        )

    print(
        "PostgreSQL Login Status:",
        postgres_response.status_code
    )

    if (
        sqlite_response.status_code == 200
        and postgres_response.status_code == 200
    ):
        print("RESULT: BOTH DATABASE LOGINS WORKING")

    elif (
        sqlite_response.status_code == 200
        and postgres_response.status_code == 401
    ):
        print(
            "RESULT: POSTGRESQL LOGIN LOGIC "
            "NEEDS INVESTIGATION"
        )

    elif (
        sqlite_response.status_code == 401
        and postgres_response.status_code == 401
    ):
        print(
            "RESULT: ADMIN CREDENTIALS REJECTED "
            "BY BOTH DATABASES"
        )

    else:
        print(
            "RESULT: DIFFERENT LOGIN BEHAVIOR "
            "- REVIEW REQUIRED"
        )

    print("\nDIAGNOSTIC COMPLETED")
    print("Passwords and tokens not displayed.")

finally:
    credentials.clear()
    del password
