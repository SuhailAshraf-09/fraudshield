import base64
import json
import time
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
REPORT = Path("reports/phase9/live_jwt_security.json")

print("\nFRAUDSHIELD AI - LIVE JWT SECURITY TEST")
print("No transaction or prediction write requests.")

# Verify live backend availability.
try:
    response = httpx.get(
        BASE + "/openapi.json",
        timeout=10
    )
    response.raise_for_status()
except httpx.HTTPError as error:
    raise SystemExit(
        "SAFETY STOP: FastAPI not available: "
        + type(error).__name__
    )

print("FastAPI Server: ONLINE")

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

with httpx.Client(timeout=15) as client:

    login = client.post(
        BASE + "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    del password

    print("Admin Login:", login.status_code)

    if login.status_code != 200:
        raise SystemExit(
            "SAFETY STOP: Admin login failed."
        )

    token = login.json().get("access_token")

    if not isinstance(token, str) or token.count(".") != 2:
        raise SystemExit(
            "SAFETY STOP: Unexpected JWT format."
        )

    header, payload, signature = token.split(".")

    if not signature:
        raise SystemExit(
            "SAFETY STOP: JWT signature missing."
        )

    # Change the signature without changing the payload.
    changed = "A" if signature[0] != "A" else "B"
    tampered = (
        header + "." + payload + "."
        + changed + signature[1:]
    )

    tests = {
        "valid_admin": {
            "headers": {
                "Authorization": "Bearer " + token
            },
            "expected": 200
        },
        "missing_token": {
            "headers": {},
            "expected": 401
        },
        "invalid_token": {
            "headers": {
                "Authorization": "Bearer invalid.test.token"
            },
            "expected": 401
        },
        "tampered_signature": {
            "headers": {
                "Authorization": "Bearer " + tampered
            },
            "expected": 401
        },
        "wrong_auth_scheme": {
            "headers": {
                "Authorization": "Basic dGVzdA=="
            },
            "expected": 401
        }
    }

    outcomes = {}

    for name, test in tests.items():
        result = client.get(
            BASE + "/api/v1/auth/me",
            headers=test["headers"]
        )

        passed = (
            result.status_code == test["expected"]
        )

        outcomes[name] = {
            "actual": result.status_code,
            "expected": test["expected"],
            "passed": passed
        }

        print("\nTest:", name)
        print("Status:", result.status_code)
        print("Expected:", test["expected"])
        print("PASS:", passed)

# Inspect expiry claim for presence and current validity.
# This local decoding does not validate the signature.
try:
    padded = payload + "=" * (-len(payload) % 4)

    claims = json.loads(
        base64.urlsafe_b64decode(
            padded.encode("ascii")
        )
    )

    exp = claims.get("exp")

    expiry_ok = (
        isinstance(exp, (int, float))
        and not isinstance(exp, bool)
        and exp > time.time()
    )

except (ValueError, TypeError, UnicodeError):
    expiry_ok = False

print("\nJWT Expiry Claim Present And Future:", expiry_ok)

passed = (
    all(item["passed"] for item in outcomes.values())
    and expiry_ok
)

REPORT.parent.mkdir(parents=True, exist_ok=True)

REPORT.write_text(
    json.dumps({
        "test": "live_jwt_authentication_security",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "http_results": outcomes,
        "expiry_claim_valid_now": expiry_ok,
        "expired_token_rejection_tested": False,
        "real_viewer_jwt_tested": False,
        "checks_passed": passed,
        "tokens_and_passwords_saved": False
    }, indent=2),
    encoding="utf-8"
)

print("\nFINAL JWT SECURITY RESULTS")
print("checks_passed:", passed)
print("Report:", REPORT)
print("Passwords and JWT tokens not saved.")
print("No database write requests submitted.")

if not passed:
    raise SystemExit("JWT SECURITY REVIEW REQUIRED")

print("\nLIVE JWT SECURITY TEST PASSED!")