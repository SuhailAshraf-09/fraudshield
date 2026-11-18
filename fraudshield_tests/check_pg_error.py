from getpass import getpass
import psycopg

print("\nFRAUDSHIELD AI - DATABASE CONNECTION CHECK")

password = getpass("PostgreSQL app password: ")

try:
    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="fraudshield_db",
        user="fraudshield_app",
        password=password,
        connect_timeout=10
    ) as connection:

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user"
            )
            result = cursor.fetchone()

        print("Connection: PASS")
        print("Database:", result[0])
        print("User:", result[1])
        print("POSTGRESQL CONNECTION VERIFIED!")

except Exception as error:
    print("Connection: FAILED")
    print("Error Type:", type(error).__name__)

    detail = str(error).replace(
        password, "[REDACTED]"
    )

    print("Actual Error:", detail[:600])
    print(
        "SQLSTATE:",
        getattr(error, "sqlstate", None)
    )

finally:
    del password

print("\nNo database records modified.")
