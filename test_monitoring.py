
import getpass
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

email = input("Admin email: ")
password = getpass.getpass("Admin password: ")

with httpx.Client(timeout=15) as client:
    login = client.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
    )

    print("Login HTTP Status:", login.status_code)

    if login.status_code != 200:
        raise SystemExit("Authentication failed.")

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    endpoints = [
        "/transactions",
        "/dashboard/summary",
    ]

    for endpoint in endpoints:
        response = client.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
        )

        print(f"\nEndpoint: {endpoint}")
        print("HTTP Status:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                print("Response fields:", list(data.keys()))
            elif isinstance(data, list):
                print("Records returned:", len(data))
        else:
            print("Request failed.")
