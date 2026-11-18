import base64
import json
import time
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx

from app import security
from app.models import User

BASE = "http://127.0.0.1:8000"
REPORT = Path("reports/phase9/expired_jwt_test.json")

print("\nFRAUDSHIELD AI - EXPIRED JWT SECURITY TEST")

# STEP 1 - Capture the signing configuration in memory
# through the existing application token issuer.
# No secret is printed or written to a file.

original_encode = security.jwt.encode
signing = {}

def capture_encoder(*args, **kwargs):
    signing["key"] = (
        args[1] if len(args) > 1
        else kwargs.get("key")
    )
    signing["algorithm"] = (
        args[2] if len(args) > 2
        else kwargs.get("algorithm")
    )
    return original_encode(*args, **kwargs)

synthetic_user = User(
    id=str(uuid4()),
    email="expiry-test@example.invalid",
    password_hash="synthetic-test-only",
    role="admin"
)

try:
    with patch.object(
        security.jwt,
        "encode",
        side_effect=capture_encoder
    ):
        security.issue_token(synthetic_user)
except Exception as exc:
    print("Token issuer check:", type(exc).__name__)
    raise SystemExit(
        "SAFETY STOP: Token issuer needs review."
    )

if not signing.get("key") or not signing.get("algorithm"):
    raise SystemExit(
        "SAFETY STOP: Signing configuration unavailable."
    )

print("Existing token issuer: VERIFIED")
print("Signing configuration: CAPTURED SECURELY")

# STEP 2 - Authenticate using real website credentials.

email = input("Website admin email: ").strip()
password = getpass("Website admin password: ")

try:
    with httpx.Client(base_url=BASE, timeout=15) as client:

        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )

        del password

        print("Admin Login Status:", login.status_code)

        if login.status_code != 200:
            raise SystemExit(
                "SAFETY STOP: Website admin login failed."
            )

        token = login.json().get("access_token", "")

        def check_token(value):
            response = client.get(
                "/api/v1/auth/me",
                headers={
                    "Authorization": "Bearer " + value
                }
            )
            return response.status_code

        original_status = check_token(token)
        print("Original Token Status:", original_status)

        if original_status != 200:
            raise SystemExit(
                "SAFETY STOP: Original token rejected."
            )

        # Decode the payload locally for test preparation.
        # Signature validation is performed by the live API.
        pieces = token.split(".")

        if len(pieces) != 3:
            raise SystemExit("Unexpected token format.")

        payload = pieces[1]
        padded = payload + "=" * (-len(payload) % 4)

        claims = json.loads(
            base64.urlsafe_b64decode(padded)
        )

        if "exp" not in claims:
            raise SystemExit(
                "SAFETY STOP: Expiry claim missing."
            )

        # STEP 3 - Verify a re-signed unmodified token.
        # This confirms local signing matches the live server.

        baseline = original_encode(
            claims,
            signing["key"],
            algorithm=signing["algorithm"]
        )

        if isinstance(baseline, bytes):
            baseline = baseline.decode("ascii")

        baseline_status = check_token(baseline)

        print("Re-signed Valid Status:", baseline_status)

        if baseline_status != 200:
            raise SystemExit(
                "SAFETY STOP: Signing configuration differs "
                "from running server. No expiry conclusion."
            )

        # STEP 4 - Generate a genuinely expired signed JWT.
        now = int(time.time())

        expired_claims = dict(claims)
        expired_claims["exp"] = now - 3600

        if "iat" in expired_claims:
            expired_claims["iat"] = now - 7200

        if "nbf" in expired_claims:
            expired_claims["nbf"] = now - 7200

        expired_token = original_encode(
            expired_claims,
            signing["key"],
            algorithm=signing["algorithm"]
        )

        if isinstance(expired_token, bytes):
            expired_token = expired_token.decode("ascii")

        expired_status = check_token(expired_token)

        print("Expired Signed Token Status:", expired_status)

        passed = (
            original_status == 200
            and baseline_status == 200
            and expired_status == 401
        )

except httpx.HTTPError as exc:
    print("Connection Error:", type(exc).__name__)
    raise SystemExit(
        "SAFETY STOP: Live API connection failed."
    )

finally:
    signing.clear()

REPORT.parent.mkdir(parents=True, exist_ok=True)

REPORT.write_text(
    json.dumps({
        "test": "signed_expired_jwt_rejection",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "original_status": original_status,
        "resigned_valid_status": baseline_status,
        "expired_status": expired_status,
        "checks_passed": passed,
        "secrets_or_tokens_saved": False
    }, indent=2),
    encoding="utf-8"
)

print("\nFINAL JWT EXPIRATION RESULTS")
print("checks_passed:", passed)
print("Report:", REPORT)
print("No transaction write requests submitted.")
print("Passwords and tokens not saved.")

if not passed:
    raise SystemExit("JWT EXPIRATION REVIEW REQUIRED")

print("\nEXPIRED JWT SECURITY TEST PASSED!")