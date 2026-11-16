"""FraudShield AI: local test of protected demo fraud-risk assessment API.

Run while the FastAPI server is running on http://127.0.0.1:8000.
Does not print credentials or JWT access tokens.
"""
from getpass import getpass
from uuid import uuid4

import httpx

BASE_URL = "http://127.0.0.1:8000"

email = input("Admin email: ").strip()
password = getpass("Admin password: ")

with httpx.Client(timeout=15) as client:
    login = client.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    print("Login HTTP status:", login.status_code)
    if login.status_code != 200:
        print("Login failed:", login.json().get("detail", "Unknown error"))
        raise SystemExit(1)

    token = login.json()["access_token"]
    payload = {
        "transaction_id": f"DEMO_{uuid4().hex[:12].upper()}",
        "amount_minor": 8500000,  # INR paise: 8500000 = INR 85,000
        "currency": "INR",
        "occurred_at": "2026-11-16T02:15:00+05:30",  # illustrative transaction time
        "merchant_category": "online_purchase",
        "features": {
            "new_device": True,
            "international": True,
            "tx_24h": 9,
            "distance_km": 800,
            "hour": 2,
        },
    }
    response = client.post(
        f"{BASE_URL}/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

print("Prediction HTTP status:", response.status_code)
result = response.json()
if response.status_code == 200:
    for key in ("transaction_id", "risk_index", "risk_tier", "requires_review", "reasons", "model_version", "demo_only"):
        print(f"{key}: {result.get(key)}")
else:
    print("API error:", result.get("detail", result))
