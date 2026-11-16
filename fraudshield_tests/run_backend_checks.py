import getpass
import httpx

BASE = "http://127.0.0.1:8000/api/v1"

email = input("Admin email: ")
password = getpass.getpass("Admin password: ")

with httpx.Client(timeout=15) as client:
    login = client.post(
        BASE + "/auth/login",
        json={"email": email, "password": password}
    )

    print("Login Status:", login.status_code)

    if login.status_code != 200:
        raise SystemExit("Authentication failed")

    token = login.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}

    endpoints = [
        "/auth/me",
        "/transactions",
        "/dashboard/summary",
        "/alerts",
        "/analytics/trends",
        "/models/metrics"
    ]

    for endpoint in endpoints:
        response = client.get(
            BASE + endpoint,
            headers=headers
        )

        print(endpoint, "HTTP Status:", response.status_code)
