"""Minimal JWT demo auth. Add SSO/MFA, rate limits and secret rotation before production."""
import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User

bearer = HTTPBearer(auto_error=False)
ITERATIONS = 600_000


def hash_password(password: str) -> str:
    if not 12 <= len(password) <= 128:
        raise ValueError("Password length must be 12–128 characters")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iterations, salt, digest = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(iterations))
        return secrets.compare_digest(actual, base64.b64decode(digest))
    except (ValueError, TypeError):
        return False


def issue_token(user: User) -> dict:
    cfg = settings()
    if len(cfg.jwt_secret) < 32 or cfg.jwt_secret.startswith("REPLACE_"):
        raise RuntimeError("Set JWT_SECRET to a unique 32+ character value in .env")
    expiry = datetime.now(timezone.utc) + timedelta(minutes=cfg.token_minutes)
    encoded = jwt.encode({"sub": user.id, "role": user.role, "exp": expiry, "iat": datetime.now(timezone.utc)}, cfg.jwt_secret, algorithm="HS256")
    return {"access_token": encoded, "token_type": "bearer", "expires_in": cfg.token_minutes * 60}


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    cfg = settings()
    if not credentials or len(cfg.jwt_secret) < 32 or cfg.jwt_secret.startswith("REPLACE_"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = jwt.decode(credentials.credentials, cfg.jwt_secret, algorithms=["HS256"], options={"require": ["exp", "sub"]})
        user = db.get(User, claims["sub"])
        if user is None or claims.get("role") != user.role:
            raise ValueError("user missing or role changed")
        return user
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})


def reviewer_or_admin(user: User = Depends(current_user)) -> User:
    if user.role not in {"reviewer", "admin"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Reviewer or admin role required")
    return user
